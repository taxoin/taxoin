"""
BranchManager: Manages branch lifecycle and operations.

Part of TODO-0002 Phase 1.3: BranchManager Implementation
"""
from __future__ import annotations

import time
from typing import Optional

from .branch_state import BranchState
from .conflict_detector import ConflictDetector, MergeResult, ResolutionStrategy
from .validator_network import ValidatorNode, ValidatorSet, ValidatorNetwork
from .core import Account, AsyncTransaction, Block, BlockHeader, Transaction, TxOutput
from .git_backend import GitBlockchain
from .mempool import Mempool
from .miner import mine_block


class BranchManager:
    """Manages transaction branches and their state.

    Responsibilities:
    - Create new branches with proper naming
    - Maintain branch state (accounts, UTXOs, mempool)
    - Submit transactions to specific branches
    - Mine blocks on branches
    - Track branch metadata
    """

    def __init__(self, repo_path: str = "."):
        self.git = GitBlockchain(repo_path)
        self.branches: dict[str, BranchState] = {}
        self._sequence_counters: dict[tuple[str, int], int] = {}  # (wallet, timestamp) -> sequence
        self._validator_network: Optional[ValidatorNetwork] = None

        # Initialize main branch state
        self._init_main_state()

    def _init_main_state(self) -> None:
        """Initialize state for the main branch."""
        main_branch = self._get_main_branch_name()

        self.branches[main_branch] = BranchState(
            branch_name=main_branch,
            parent_hash="0" * 64,
            accounts={},
            utxo_set={},
            mempool=Mempool(),
            created_at=time.time(),
            last_updated=time.time(),
            transaction_count=0,
            spent_utxos=set(),
            used_nonces={},
        )

    def _get_main_branch_name(self) -> str:
        """Get the name of the main branch (master or main)."""
        branches = self.git.list_branches()
        if "main" in branches:
            return "main"
        elif "master" in branches:
            return "master"
        else:
            # Default to main if no branches exist yet
            return "main"

    def _get_next_sequence(self, wallet: str, timestamp: int) -> int:
        """Get next sequence number for a wallet at a given timestamp.

        Args:
            wallet: Wallet address
            timestamp: Unix timestamp

        Returns:
            Sequence number (0-999)
        """
        key = (wallet, timestamp)
        if key not in self._sequence_counters:
            self._sequence_counters[key] = 0
        else:
            self._sequence_counters[key] += 1
        return self._sequence_counters[key]

    def create_branch(self, wallet: str, parent_branch: str = None) -> str:
        """Create a new transaction branch for a wallet.

        Args:
            wallet: Wallet address (owner of the branch)
            parent_branch: Parent branch to clone from (default: main)

        Returns:
            Branch name in format: branch/{wallet}/{timestamp}_{sequence}
        """
        if parent_branch is None:
            parent_branch = self._get_main_branch_name()

        # Generate branch name
        timestamp = int(time.time())
        sequence = self._get_next_sequence(wallet, timestamp)
        branch_name = f"branch/{wallet}/{timestamp}_{sequence:03d}"

        # Get parent state
        parent_state = self.branches.get(parent_branch)
        if not parent_state:
            raise ValueError(f"Parent branch '{parent_branch}' does not exist")

        # Clone parent state
        branch_state = parent_state.clone()
        branch_state.branch_name = branch_name
        branch_state.parent_hash = self.git.get_branch_head(parent_branch)

        # Create git branch
        self.git.create_branch(branch_name, from_ref=parent_branch)

        # Store branch state
        self.branches[branch_name] = branch_state

        # Store metadata
        metadata = {
            "owner": wallet,
            "created_at": timestamp,
            "status": "active",
            "parent_branch": parent_branch,
        }
        self.git.set_branch_metadata(branch_name, metadata)

        return branch_name

    async def submit_tx_to_branch(
        self,
        branch_name: str,
        tx: AsyncTransaction
    ) -> tuple[bool, str]:
        """Submit a transaction to a specific branch.

        Args:
            branch_name: Name of the branch
            tx: Transaction to submit

        Returns:
            Tuple of (success, message)
        """
        # Get branch state
        branch_state = self.branches.get(branch_name)
        if not branch_state:
            return False, f"Branch '{branch_name}' does not exist"

        # Get sender account
        sender_acct = branch_state.accounts.get(tx.sender)
        if not sender_acct:
            return False, f"Sender {tx.sender} does not exist on {branch_name}"

        # Validate transaction
        valid, msg = branch_state.mempool.validate_tx(
            tx, sender_acct.balance, sender_acct.nonce
        )
        if not valid:
            return False, msg

        # Submit to mempool
        success = await branch_state.mempool.submit(tx)
        return success, "ok" if success else "failed to submit"

    def mine_block_on_branch(
        self,
        branch_name: str,
        coinbase_address: str
    ) -> Optional[Block]:
        """Mine a new block on a specific branch.

        Args:
            branch_name: Name of the branch
            coinbase_address: Address to receive mining reward

        Returns:
            Mined block, or None if mining failed
        """
        # Get branch state
        branch_state = self.branches.get(branch_name)
        if not branch_state:
            return None

        # Switch to branch
        try:
            self.git.switch_branch(branch_name)
        except Exception:
            return None

        # Get pending transactions
        pending_txs = branch_state.mempool.get_pending_transactions()
        account_txs = [tx for tx in pending_txs if isinstance(tx, AsyncTransaction)]

        # Create coinbase transaction
        reward = 50.0
        coinbase_tx = Transaction.coinbase(coinbase_address, reward)

        # Build state snapshot
        state_snapshot = {}
        for addr, acct in branch_state.accounts.items():
            state_snapshot[addr] = acct.balance

        # Apply transactions to snapshot
        for tx in account_txs:
            if tx.sender not in state_snapshot:
                continue
            if tx.recipient not in state_snapshot:
                state_snapshot[tx.recipient] = 0.0

            total_cost = tx.value + (tx.gas_price * tx.gas_limit)
            if state_snapshot[tx.sender] >= total_cost:
                state_snapshot[tx.sender] -= total_cost
                state_snapshot[tx.recipient] += tx.value

                # Gas fees to miner
                if coinbase_address not in state_snapshot:
                    state_snapshot[coinbase_address] = 0.0
                state_snapshot[coinbase_address] += (tx.gas_price * tx.gas_limit)

        # Add coinbase reward
        if coinbase_address in state_snapshot:
            state_snapshot[coinbase_address] += reward
        else:
            state_snapshot[coinbase_address] = reward

        # Create block
        from .core import sha256
        parent_hash = self.git.get_branch_head(branch_name)
        all_txs = [coinbase_tx] + account_txs
        merkle = sha256("".join(
            t.tx_hash if hasattr(t, "tx_hash") else t.tx_id for t in all_txs
        ))

        header = BlockHeader(
            parent_hash=parent_hash,
            merkle_root=merkle,
            timestamp=time.time(),
            difficulty=4,  # TODO: dynamic difficulty
        )

        block = Block(
            header=header,
            transactions=all_txs,
            state_snapshot=state_snapshot,
        )

        # Mine block
        try:
            mine_block(header)
        except RuntimeError:
            return None

        # Commit to git
        self.git.add_block(block)

        # Update branch state
        for addr, balance in state_snapshot.items():
            if addr not in branch_state.accounts:
                branch_state.accounts[addr] = Account(address=addr)
            branch_state.accounts[addr].balance = balance

        # Update nonces
        for tx in account_txs:
            if tx.sender in branch_state.accounts:
                branch_state.accounts[tx.sender].nonce = max(
                    branch_state.accounts[tx.sender].nonce,
                    tx.nonce + 1
                )
            branch_state.track_used_nonce(tx.sender, tx.nonce)

        # Clear mempool
        confirmed = set()
        for tx in all_txs:
            h = tx.tx_hash if hasattr(tx, "tx_hash") else tx.tx_id
            confirmed.add(h)
        branch_state.mempool.remove_confirmed(confirmed)

        # Update metadata
        branch_state.last_updated = time.time()
        branch_state.transaction_count += len(account_txs)

        return block

    def list_branches(self) -> list[str]:
        """List all branches.

        Returns:
            List of branch names
        """
        return self.git.list_branches()

    def get_branch_state(self, branch_name: str) -> Optional[BranchState]:
        """Get state for a specific branch.

        Args:
            branch_name: Name of the branch

        Returns:
            BranchState or None if branch doesn't exist
        """
        return self.branches.get(branch_name)

    def get_main_state(self) -> BranchState:
        """Get state for the main branch.

        Returns:
            Main branch state
        """
        main_branch = self._get_main_branch_name()
        return self.branches[main_branch]

    def merge_branch(
        self,
        source: str,
        target: str | None = None,
        strategy: ResolutionStrategy = ResolutionStrategy.ABORT,
    ) -> MergeResult:
        """Merge a source branch into a target branch with conflict detection.

        Before performing the git merge, runs application-level conflict
        detection on the branch states. If conflicts are found, the
        resolution strategy determines whether to abort, prefer one side,
        or raise for manual intervention.

        Args:
            source: Name of the source branch to merge from
            target: Name of the target branch (default: main/master)
            strategy: Resolution strategy for conflicts

        Returns:
            MergeResult indicating success/failure

        Raises:
            MergeConflictError: If strategy is MANUAL and conflicts exist
            ValueError: If source or target branch doesn't exist
        """
        if target is None:
            target = self._get_main_branch_name()

        # Validate branches exist
        source_state = self.branches.get(source)
        if not source_state:
            return MergeResult(
                success=False,
                message=f"Source branch '{source}' does not exist",
            )

        target_state = self.branches.get(target)
        if not target_state:
            return MergeResult(
                success=False,
                message=f"Target branch '{target}' does not exist",
            )

        # Run conflict detection
        conflicts = ConflictDetector.detect_all(source_state, target_state)

        # Resolve (or abort)
        if conflicts:
            result = ConflictDetector.resolve(conflicts, strategy)
            if not result.success:
                return result
            # PREFER_SOURCE / PREFER_TARGET: continue with merge

        # Perform git-level merge
        try:
            merge_commit = self.git.merge_branches(source, target, strategy="ours")
        except Exception as e:
            return MergeResult(
                success=False,
                message=f"Git merge failed: {e}",
            )

        # Apply source branch state to target
        source_state = self.branches[source]

        # Merge accounts: source values overwrite target for PREFER_SOURCE,
        # or keep target values for PREFER_TARGET
        if strategy in (ResolutionStrategy.PREFER_SOURCE, ResolutionStrategy.ABORT):
            # ABORT with no conflicts: merge normally (source adds to target)
            for addr, acct in source_state.accounts.items():
                target_state.accounts[addr] = Account(
                    address=acct.address,
                    balance=acct.balance,
                    nonce=max(
                        acct.nonce,
                        target_state.accounts.get(addr, Account(addr)).nonce,
                    ),
                )

            # Merge UTXOs
            for outpoint, utxo in source_state.utxo_set.items():
                if outpoint not in target_state.utxo_set:
                    target_state.utxo_set[outpoint] = utxo

            # Merge spent_utxos and used_nonces
            target_state.spent_utxos.update(source_state.spent_utxos)
            for addr, nonces in source_state.used_nonces.items():
                if addr not in target_state.used_nonces:
                    target_state.used_nonces[addr] = set()
                target_state.used_nonces[addr].update(nonces)

        elif strategy == ResolutionStrategy.PREFER_TARGET:
            # Keep target state as-is — nothing to merge state-wise
            pass

        target_state.transaction_count += source_state.transaction_count
        target_state.last_updated = source_state.last_updated

        # Clean up source branch state
        self.branches.pop(source, None)

        return MergeResult(
            success=True,
            merge_commit=merge_commit,
            conflicts=conflicts,
            message=f"Successfully merged '{source}' into '{target}'",
        )

    # ── Validator Network Integration ─────────────────────────────────

    def init_validator_network(self, count: int = 7) -> None:
        """Initialize a validator network with the given number of validators.

        Args:
            count: Number of validators to create (default: 7)
        """
        validators: list[ValidatorNode] = []
        private_keys: dict[str, str] = {}

        for _ in range(count):
            node, priv_key_pem = ValidatorNode.generate_with_private_key()
            validators.append(node)
            private_keys[node.address] = priv_key_pem

        vset = ValidatorSet(validators)
        self._validator_network = ValidatorNetwork(vset, private_keys)

    def get_validators(self) -> list[ValidatorNode]:
        """Get all validators in the network.

        Returns:
            List of validator nodes, or empty list if network not initialized
        """
        if not self._validator_network:
            return []
        return self._validator_network.validator_set.get_active_validators()
