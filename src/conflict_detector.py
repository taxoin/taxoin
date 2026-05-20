"""
ConflictDetector: Cross-branch conflict detection and resolution.

Part of TODO-0002 Phase 2: Conflict Detection
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from .branch_state import BranchState
from .core import Account


class ConflictType(Enum):
    """Types of conflicts that can occur between branches."""
    UTXO_DOUBLE_SPEND = "utxo_double_spend"
    NONCE_COLLISION = "nonce_collision"
    BALANCE_MISMATCH = "balance_mismatch"


@dataclass
class Conflict:
    """A single conflict between two branch states."""
    conflict_type: ConflictType
    detail: str
    branch_value: Any = None
    main_value: Any = None
    address: Optional[str] = None
    outpoint: Optional[tuple] = None


class ResolutionStrategy(Enum):
    """Strategies for resolving detected conflicts."""
    ABORT = "abort"
    PREFER_SOURCE = "source"
    PREFER_TARGET = "target"
    MANUAL = "manual"


@dataclass
class MergeResult:
    """Result of a merge operation."""
    success: bool
    merge_commit: Optional[str] = None
    conflicts: list[Conflict] = field(default_factory=list)
    message: str = ""


class MergeConflictError(Exception):
    """Raised when merge is aborted due to conflicts with MANUAL strategy."""
    def __init__(self, message: str, conflicts: list[Conflict]):
        self.conflicts = conflicts
        super().__init__(message)


class ConflictDetector:
    """Stateless conflict detection and resolution between branch states."""

    @staticmethod
    def detect_utxo_conflicts(branch: BranchState, target: BranchState) -> list[Conflict]:
        """Detect UTXO double-spend conflicts between two branches.

        A double-spend occurs when the same UTXO outpoint appears in
        both branches' spent_utxos sets.

        Args:
            branch: Source branch state
            target: Target branch state

        Returns:
            List of detected conflicts
        """
        conflicts: list[Conflict] = []

        # Double-spend detection: intersection of spent_utxos sets
        double_spent = branch.spent_utxos & target.spent_utxos
        for outpoint in double_spent:
            utxo = branch.utxo_set.get(outpoint)
            amount = utxo.amount if utxo else 0
            address = utxo.address if utxo else "unknown"
            detail = (
                f"UTXO {outpoint[0]}:{outpoint[1]} "
                f"({amount} coins to {address}) "
                f"spent in both branches"
            )
            conflicts.append(Conflict(
                conflict_type=ConflictType.UTXO_DOUBLE_SPEND,
                detail=detail,
                outpoint=outpoint,
                branch_value=utxo,
                main_value=target.utxo_set.get(outpoint),
            ))

        return conflicts

    @staticmethod
    def detect_nonce_conflicts(branch: BranchState, target: BranchState) -> list[Conflict]:
        """Detect nonce collision conflicts between two branches.

        A nonce collision occurs when the same address uses the same nonce
        value in both branches.

        Args:
            branch: Source branch state
            target: Target branch state

        Returns:
            List of detected conflicts
        """
        conflicts: list[Conflict] = []

        for address, branch_nonces in branch.used_nonces.items():
            target_nonces = target.used_nonces.get(address)
            if target_nonces is None:
                continue

            collided = branch_nonces & target_nonces
            if collided:
                detail = (
                    f"Nonce collision for {address}: "
                    f"nonces {sorted(collided)} used in both branches"
                )
                conflicts.append(Conflict(
                    conflict_type=ConflictType.NONCE_COLLISION,
                    detail=detail,
                    address=address,
                    branch_value=branch_nonces,
                    main_value=target_nonces,
                ))

        return conflicts

    @staticmethod
    def detect_balance_conflicts(branch: BranchState, target: BranchState) -> list[Conflict]:
        """Detect balance mismatch conflicts between two branches.

        Only addresses present in BOTH branches are compared.
        An address in only one branch is not a conflict (it is a new account).

        Args:
            branch: Source branch state
            target: Target branch state

        Returns:
            List of detected conflicts
        """
        conflicts: list[Conflict] = []

        common_addresses = set(branch.accounts.keys()) & set(target.accounts.keys())
        for address in common_addresses:
            branch_acct = branch.accounts[address]
            target_acct = target.accounts[address]

            if branch_acct.balance != target_acct.balance:
                detail = (
                    f"Balance mismatch for {address}: "
                    f"{branch_acct.balance} (branch) vs {target_acct.balance} (target)"
                )
                conflicts.append(Conflict(
                    conflict_type=ConflictType.BALANCE_MISMATCH,
                    detail=detail,
                    address=address,
                    branch_value=branch_acct.balance,
                    main_value=target_acct.balance,
                ))

        return conflicts

    @staticmethod
    def detect_all(branch: BranchState, target: BranchState) -> list[Conflict]:
        """Run all conflict detectors and return combined results.

        Results are ordered by severity: UTXO > Nonce > Balance.

        Args:
            branch: Source branch state
            target: Target branch state

        Returns:
            Combined list of all detected conflicts
        """
        conflicts: list[Conflict] = []
        conflicts.extend(ConflictDetector.detect_utxo_conflicts(branch, target))
        conflicts.extend(ConflictDetector.detect_nonce_conflicts(branch, target))
        conflicts.extend(ConflictDetector.detect_balance_conflicts(branch, target))
        return conflicts

    @staticmethod
    def resolve(
        conflicts: list[Conflict],
        strategy: ResolutionStrategy,
    ) -> MergeResult:
        """Resolve a list of conflicts using the given strategy.

        Args:
            conflicts: List of conflicts to resolve
            strategy: Resolution strategy to apply

        Returns:
            MergeResult indicating success/failure

        Raises:
            MergeConflictError: If strategy is MANUAL and conflicts exist
        """
        if not conflicts:
            return MergeResult(success=True, message="No conflicts")

        if strategy == ResolutionStrategy.ABORT:
            return MergeResult(
                success=False,
                conflicts=conflicts,
                message=f"Aborted: {len(conflicts)} conflict(s) detected",
            )

        if strategy == ResolutionStrategy.MANUAL:
            detail = "; ".join(c.detail for c in conflicts)
            raise MergeConflictError(
                f"Manual resolution required: {len(conflicts)} conflict(s): {detail}",
                conflicts=conflicts,
            )

        # PREFER_SOURCE or PREFER_TARGET — proceed (caller applies the values)
        side = "source" if strategy == ResolutionStrategy.PREFER_SOURCE else "target"
        return MergeResult(
            success=True,
            conflicts=conflicts,
            message=f"Resolved {len(conflicts)} conflict(s) by preferring {side}",
        )
