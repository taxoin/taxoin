"""
Git-based blockchain backend.

Each block is stored as a git commit:
  - The git tree contains `block.json` with the full block data
  - The commit message is the block hash + metadata
  - Parent commit = previous block hash
  - Branch HEAD always points to the latest block
  - Tags mark checkpoints (genesis, milestones)

Concept:
  Blockchain          → Git
  Block               → Commit
  Parent hash         → Parent commit SHA
  Block hash (PoW)    → Signed tag / annotated tag with hash
  Merkle Root         → Git tree SHA (or we embed it in the tree)
  Chain               → Branch history (git log)
"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from .core import Block, BlockHeader, make_genesis_block


GIT_DIR = ".gitchain"
BLOCK_FILE = "block.json"
GENESIS_TAG = "genesis"


class GitBackendError(RuntimeError):
    pass


def _git(*args: str, cwd: str) -> str:
    """Run a git command in the given working directory."""
    try:
        result = subprocess.run(
            ["git"] + list(args),
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            raise GitBackendError(
                f"git {' '.join(args)} failed: {result.stderr.strip()}"
            )
        return result.stdout.strip()
    except FileNotFoundError:
        raise GitBackendError("git is not installed on this system")
    except subprocess.TimeoutExpired:
        raise GitBackendError("git command timed out")


class GitBlockchain:
    """Blockchain backed by a git repository."""

    def __init__(self, repo_path: str = ".", chain_dir: str = GIT_DIR):
        self.repo_path = os.path.abspath(repo_path)
        self.chain_dir = os.path.join(self.repo_path, chain_dir)
        self.chain_dir_rel = GIT_DIR  # relative path for git show commands
        self._init_repo()

    # ── Repo management ──────────────────────────────────────────────

    def _init_repo(self) -> None:
        """Ensure the git repo and .gitchain dir exist."""
        os.makedirs(self.chain_dir, exist_ok=True)
        if not os.path.exists(os.path.join(self.repo_path, ".git")):
            _git("init", cwd=self.repo_path)
            _git("config", "user.name", "gitchain", cwd=self.repo_path)
            _git("config", "user.email", "gitchain@localhost", cwd=self.repo_path)
            # Generate initial genesis block
            genesis = make_genesis_block()
            self._store_block(genesis, parent_commit=None)

    def _current_head(self) -> Optional[str]:
        """Return the commit SHA at HEAD, or None if no commits."""
        try:
            return _git("rev-parse", "HEAD", cwd=self.repo_path)
        except GitBackendError:
            return None

    # ── Block storage ────────────────────────────────────────────────

    def _write_block_file(self, block: Block) -> str:
        """Write block.json inside .gitchain/ and return the full path."""
        block_path = os.path.join(self.chain_dir, BLOCK_FILE)
        with open(block_path, "w") as f:
            f.write(block.serialize())
        return block_path

    def _read_block_file(self) -> Optional[Block]:
        """Read block.json from .gitchain/ and return a Block."""
        block_path = os.path.join(self.chain_dir, BLOCK_FILE)
        if not os.path.exists(block_path):
            return None
        with open(block_path) as f:
            data = json.load(f)
        header = BlockHeader(**data["header"])
        return Block(
            header=header,
            transactions=data.get("transactions", []),
            state_snapshot=data.get("state_snapshot", {}),
        )

    def _store_block(self, block: Block, parent_commit: Optional[str]) -> str:
        """Commit the block into git, return the commit SHA."""
        self._write_block_file(block)
        _git("add", os.path.join(self.chain_dir, BLOCK_FILE), cwd=self.repo_path)

        commit_msg = (
            f"BLOCK {block.hash}\n"
            f"Parent: {parent_commit or 'genesis'}\n"
            f"Difficulty: {block.header.difficulty}\n"
            f"Nonce: {block.header.nonce}\n"
            f"Txs: {len(block.transactions)}"
        )

        # Set GIT_AUTHOR_DATE / GIT_COMMITTER_DATE for block timestamp.
        # Genesis block has timestamp=0 — git rejects 0, so skip env vars for it.
        env = os.environ.copy()
        ts = int(block.header.timestamp)
        if ts > 0:
            fmt = f"@{ts} +0000"
            env["GIT_AUTHOR_DATE"] = fmt
            env["GIT_COMMITTER_DATE"] = fmt

        try:
            result = subprocess.run(
                ["git", "commit", "--allow-empty", "-m", commit_msg],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10,
                env=env,
            )
            if result.returncode != 0:
                raise GitBackendError(result.stderr.strip())
            sha_out = result.stdout.strip()
            # Extract commit SHA from output like "[main <sha>] message"
            for word in sha_out.split():
                if len(word) == 40 and all(c in "0123456789abcdef" for c in word):
                    return word
            return _git("rev-parse", "HEAD", cwd=self.repo_path)
        except subprocess.TimeoutExpired:
            raise GitBackendError("git commit timed out")

    # ── Public API ────────────────────────────────────────────────────

    def add_block(self, block: Block) -> str:
        """Store a block as a git commit. Returns commit SHA."""
        parent = self._current_head()
        return self._store_block(block, parent)

    def get_latest_block(self) -> Optional[Block]:
        """Read the latest block from .gitchain/block.json."""
        block = self._read_block_file()
        return block

    def get_chain_height(self) -> int:
        """Number of blocks in the chain (commits on current branch)."""
        try:
            count = _git("rev-list", "--count", "HEAD", cwd=self.repo_path)
            return int(count)
        except GitBackendError:
            return 0

    def get_block_by_hash(self, block_hash: str) -> Optional[dict]:
        """Read block.json at a specific commit."""
        try:
            raw = subprocess.run(
                ["git", "show", f"{block_hash}:{self.chain_dir_rel}/{BLOCK_FILE}"],
                cwd=self.repo_path,
                capture_output=True, text=True, timeout=10,
            )
            if raw.returncode != 0:
                return None
            return json.loads(raw.stdout)
        except (subprocess.TimeoutExpired, json.JSONDecodeError):
            return None

    def verify_chain(self) -> bool:
        """Verify the entire chain's integrity."""
        try:
            log = _git("log", "--oneline", "--format=%H %P", cwd=self.repo_path)
        except GitBackendError:
            return False

        commits = log.strip().split("\n") if log.strip() else []
        for i, line in enumerate(commits):
            parts = line.split()
            commit_hash = parts[0]
            parent_hash = parts[1] if len(parts) > 1 else None

            # Verify we can read the block at this commit
            block_data = self.get_block_by_hash(commit_hash)
            if block_data is None and i > 0:
                return False  # genesis commit may not have block.json

            # Verify parent linkage
            if parent_hash and parent_hash != "0" * 40:
                parent_data = self.get_block_by_hash(parent_hash)
                if parent_data is None:
                    return False

        return True

    def get_chain_summary(self) -> list[dict]:
        """Return a list of all blocks with commit SHA and hash."""
        try:
            log = _git("log", "--format=%H", cwd=self.repo_path)
        except GitBackendError:
            return []

        shas = log.strip().split("\n") if log.strip() else []
        blocks = []
        for sha in reversed(shas):
            data = self.get_block_by_hash(sha)
            if data and "header" in data:
                hdr = data["header"]
                # Recompute hash from header fields (stored separately in JSON)
                from .core import BlockHeader as BH
                header_obj = BH(
                    parent_hash=hdr["parent_hash"],
                    merkle_root=hdr["merkle_root"],
                    timestamp=hdr["timestamp"],
                    difficulty=hdr["difficulty"],
                    nonce=hdr.get("nonce", 0),
                    version=hdr.get("version", 1),
                )
                blocks.append({
                    "commit": sha,
                    "hash": header_obj.hash(),
                    "difficulty": hdr["difficulty"],
                    "nonce": hdr.get("nonce", 0),
                    "tx_count": len(data.get("transactions", [])),
                })
            else:
                blocks.append({
                    "commit": sha, "hash": "", "difficulty": "", "nonce": "",
                    "tx_count": 0,
                })
        return blocks
