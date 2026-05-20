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


GIT_DIR = ".taxoin"
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
        """Ensure the git repo and .taxoin dir exist."""
        os.makedirs(self.chain_dir, exist_ok=True)
        if not os.path.exists(os.path.join(self.repo_path, ".git")):
            _git("init", cwd=self.repo_path)
            _git("config", "user.name", "taxoin", cwd=self.repo_path)
            _git("config", "user.email", "taxoin@localhost", cwd=self.repo_path)
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
        """Write block.json inside .taxoin/ and return the full path."""
        block_path = os.path.join(self.chain_dir, BLOCK_FILE)
        with open(block_path, "w") as f:
            f.write(block.serialize())
        return block_path

    def _read_block_file(self) -> Optional[Block]:
        """Read block.json from .taxoin/ and return a Block."""
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
        """Read the latest block from .taxoin/block.json."""
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

    # ── Branch Management (TODO-0002 Phase 1.1) ──────────────────────

    def create_branch(self, branch_name: str, from_ref: str = "HEAD") -> str:
        """Create a new git branch from a reference.

        Args:
            branch_name: Name of the new branch
            from_ref: Reference to branch from (commit SHA, branch name, or HEAD)

        Returns:
            The branch name

        Raises:
            GitBackendError: If branch already exists or creation fails
        """
        try:
            _git("branch", branch_name, from_ref, cwd=self.repo_path)
            return branch_name
        except GitBackendError as e:
            if "already exists" in str(e):
                raise GitBackendError(f"Branch '{branch_name}' already exists")
            raise

    def switch_branch(self, branch_name: str) -> None:
        """Switch to a different branch.

        Args:
            branch_name: Name of the branch to switch to

        Raises:
            GitBackendError: If branch doesn't exist or switch fails
        """
        _git("checkout", branch_name, cwd=self.repo_path)

    def list_branches(self) -> list[str]:
        """List all branches in the repository.

        Returns:
            List of branch names
        """
        try:
            output = _git("branch", "--list", cwd=self.repo_path)
            branches = []
            for line in output.split("\n"):
                line = line.strip()
                if line:
                    # Remove * prefix from current branch
                    branch = line.lstrip("* ")
                    branches.append(branch)
            return branches
        except GitBackendError:
            return []

    def get_current_branch(self) -> str:
        """Get the name of the current branch.

        Returns:
            Current branch name

        Raises:
            GitBackendError: If not on a branch (detached HEAD)
        """
        return _git("rev-parse", "--abbrev-ref", "HEAD", cwd=self.repo_path)

    def delete_branch(self, branch_name: str, force: bool = False) -> None:
        """Delete a branch.

        Args:
            branch_name: Name of the branch to delete
            force: If True, force delete even if not fully merged

        Raises:
            GitBackendError: If branch doesn't exist or is current branch
        """
        flag = "-D" if force else "-d"
        _git("branch", flag, branch_name, cwd=self.repo_path)

    def get_branch_head(self, branch_name: str) -> str:
        """Get the commit SHA at the head of a branch.

        Args:
            branch_name: Name of the branch

        Returns:
            Commit SHA (40 hex chars)

        Raises:
            GitBackendError: If branch doesn't exist
        """
        return _git("rev-parse", branch_name, cwd=self.repo_path)

    def merge_branches(self, source: str, target: str,
                      strategy: str = "ours") -> str:
        """Merge source branch into target branch.

        Args:
            source: Source branch name
            target: Target branch name
            strategy: Merge strategy (default: "ours")

        Returns:
            Commit SHA of the merge commit

        Raises:
            GitBackendError: If merge fails or conflicts occur
        """
        # Switch to target branch
        self.switch_branch(target)

        # Merge with strategy
        try:
            _git("merge", source, "-X", strategy,
                 "-m", f"Merge {source} into {target}",
                 cwd=self.repo_path)
            return _git("rev-parse", "HEAD", cwd=self.repo_path)
        except GitBackendError as e:
            # Abort merge on conflict
            try:
                _git("merge", "--abort", cwd=self.repo_path)
            except GitBackendError:
                pass
            raise GitBackendError(f"Merge conflict: {e}")

    def get_divergence(self, branch1: str, branch2: str) -> tuple[int, int]:
        """Get number of commits ahead/behind between two branches.

        Args:
            branch1: First branch name
            branch2: Second branch name

        Returns:
            Tuple of (commits_ahead, commits_behind)
            - commits_ahead: commits in branch1 not in branch2
            - commits_behind: commits in branch2 not in branch1
        """
        try:
            # Commits in branch1 not in branch2
            ahead = _git("rev-list", "--count", f"{branch2}..{branch1}",
                        cwd=self.repo_path)
            # Commits in branch2 not in branch1
            behind = _git("rev-list", "--count", f"{branch1}..{branch2}",
                         cwd=self.repo_path)
            return int(ahead), int(behind)
        except GitBackendError:
            return 0, 0

    def set_branch_metadata(self, branch_name: str, metadata: dict) -> None:
        """Store metadata for a branch using git notes.

        Args:
            branch_name: Name of the branch
            metadata: Dictionary of metadata to store
        """
        notes_json = json.dumps(metadata)

        # Get branch head commit
        try:
            commit_sha = self.get_branch_head(branch_name)
        except GitBackendError:
            raise GitBackendError(f"Branch '{branch_name}' does not exist")

        # Write to temp file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write(notes_json)
            temp_path = f.name

        try:
            _git("notes", "add", "-f", "-F", temp_path, commit_sha,
                 cwd=self.repo_path)
        finally:
            os.unlink(temp_path)

    def get_branch_metadata(self, branch_name: str) -> dict:
        """Get metadata for a branch from git notes.

        Args:
            branch_name: Name of the branch

        Returns:
            Dictionary of metadata, or empty dict if no metadata exists
        """
        try:
            commit_sha = self.get_branch_head(branch_name)
            notes = _git("notes", "show", commit_sha, cwd=self.repo_path)
            return json.loads(notes)
        except (GitBackendError, json.JSONDecodeError):
            return {}
