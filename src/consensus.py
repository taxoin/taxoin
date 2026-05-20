"""
MergeConsensus: Tendermint-style consensus for merge proposals.

Part of TODO-0002 Phase 4: Consensus Protocol
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional

from .conflict_detector import ConflictDetector, MergeResult, ResolutionStrategy


class Vote(Enum):
    YES = "yes"
    NO = "no"


class ConsensusStatus(Enum):
    PROPOSE = "propose"
    PREVOTE = "prevote"
    PRECOMMIT = "precommit"
    COMMIT = "commit"
    TIMEOUT = "timeout"
    REJECTED = "rejected"


@dataclass
class ConsensusRound:
    """State of a single consensus round."""

    proposal: "MergeProposal"  # noqa: F821 — imported at runtime
    round_id: int
    status: ConsensusStatus
    prevotes: dict[str, str] = field(default_factory=dict)
    precommits: dict[str, str] = field(default_factory=dict)
    result: Optional[MergeResult] = None
    started_at: float = 0.0


def _default_validate_fn(
    proposal: "MergeProposal",
    validator: "ValidatorNode",
    branch_state: "BranchState",
    main_state: "BranchState",
    validator_network: "ValidatorNetwork",
) -> str:
    """Default validation function for validators.

    Checks:
    1. Proposal signature validity
    2. Conflict detection between branch and main state

    Returns "yes" if all checks pass, "no" otherwise.
    """
    # Verify proposal signature
    proposer = validator_network.validator_set.get_validator(proposal.proposer)
    if proposer is None:
        return "no"

    proposal_data = (
        f"{proposal.branch_name}{proposal.parent_hash}"
        f"{proposal.final_state_hash}{proposal.transaction_count}"
    )

    from .validator_network import ValidatorNode as VN
    valid_sig = VN.verify_signature(
        proposal_data, proposal.signature, proposer.public_key
    )
    if not valid_sig:
        return "no"

    # Run conflict detection
    conflicts = ConflictDetector.detect_all(branch_state, main_state)

    # For ABORT strategy, any conflict → vote NO
    if conflicts:
        return "no"

    return "yes"


class MergeConsensus:
    """Tendermint-style consensus for merge proposals.

    Protocol flow:
    PROPOSE → PREVOTE → PRECOMMIT → COMMIT

    At each phase, 2f+1 quorum is required to progress.
    """

    def __init__(self, validator_network: "ValidatorNetwork"):  # noqa: F821
        self.validator_network = validator_network

    def propose(
        self,
        branch_state: "BranchState",
        branch_name: str,
        proposer: str,
    ) -> ConsensusRound:
        """Create and broadcast a merge proposal.

        Args:
            branch_state: State of the branch to merge
            branch_name: Name of the branch
            proposer: Validator address making the proposal

        Returns:
            A new ConsensusRound in PROPOSE status
        """
        # Create signed proposal via the network
        proposal = self.validator_network.propose_merge(
            branch_name=branch_name,
            proposer=proposer,
            branch_state=branch_state,
        )

        round = ConsensusRound(
            proposal=proposal,
            round_id=1,
            status=ConsensusStatus.PROPOSE,
            started_at=time.time(),
        )

        # Broadcast proposal to all validators
        self.validator_network.broadcast(proposal)

        return round

    def prevote_phase(
        self,
        round: ConsensusRound,
        validator_network: "ValidatorNetwork",
        validate_fn: Callable | None = None,
        branch_state: "BranchState" | None = None,
        main_state: "BranchState" | None = None,
    ) -> ConsensusRound:
        """Run the prevote phase.

        Each validator votes YES/NO based on validate_fn results.
        Progresses to PRECOMMIT if 2f+1 YES votes are collected.

        Args:
            round: The current consensus round
            validator_network: Network to collect votes from
            validate_fn: Custom validation function, or None for default
            branch_state: Branch state (for default validation)
            main_state: Main branch state (for default validation)

        Returns:
            Updated ConsensusRound
        """
        round.status = ConsensusStatus.PREVOTE

        if validate_fn is None:
            if branch_state is None or main_state is None:
                round.status = ConsensusStatus.REJECTED
                round.result = MergeResult(
                    success=False,
                    message="Missing branch state for validation",
                )
                return round

            # Use default validation with closure
            vn = validator_network
            bs = branch_state
            ms = main_state

            def default_vote_fn(proposal, validator):
                return _default_validate_fn(
                    proposal, validator, bs, ms, vn
                )

            validate_fn = default_vote_fn

        # Collect votes
        votes = validator_network.collect_votes(round.proposal, validate_fn)
        round.prevotes.update(votes)

        # Check quorum: count YES votes
        yes_addresses = [
            addr for addr, vote in round.prevotes.items()
            if vote == "yes"
        ]
        quorum_achieved = validator_network.validator_set.is_quorum_achieved(
            yes_addresses
        )

        if quorum_achieved:
            round.status = ConsensusStatus.PRECOMMIT
        else:
            round.status = ConsensusStatus.REJECTED
            round.result = MergeResult(
                success=False,
                message=f"Prevote failed: {len(yes_addresses)} YES votes "
                        f"(need {validator_network.validator_set.get_quorum_size()})",
                conflicts=[],
            )

        return round

    def precommit_phase(
        self,
        round: ConsensusRound,
        validator_network: "ValidatorNetwork",
        precommit_fn: Callable | None = None,
    ) -> ConsensusRound:
        """Run the precommit phase.

        Validators sign precommit messages.
        Progresses to COMMIT if 2f+1 precommits collected.

        Args:
            round: The current consensus round
            validator_network: Network for validator access
            precommit_fn: Custom function returning "yes"/"no" per validator,
                         or None for all-yes

        Returns:
            Updated ConsensusRound
        """
        round.status = ConsensusStatus.PRECOMMIT

        # Collect precommits from active validators
        for validator in validator_network.validator_set.get_active_validators():
            if precommit_fn is not None:
                result = precommit_fn(round.proposal, validator)
            else:
                result = "yes"

            if result == "yes":
                private_key = validator_network._private_keys.get(validator.address)
                if private_key:
                    from .validator_network import ValidatorNode as VN
                    precommit_data = (
                        f"{round.proposal.branch_name}"
                        f"{round.proposal.final_state_hash}"
                        f"{round.round_id}"
                    )
                    sig = VN.sign_data(precommit_data, private_key)
                    round.precommits[validator.address] = sig

        # Check quorum
        precommit_addresses = list(round.precommits.keys())
        quorum_achieved = validator_network.validator_set.is_quorum_achieved(
            precommit_addresses
        )

        if quorum_achieved:
            round.status = ConsensusStatus.COMMIT
        else:
            round.status = ConsensusStatus.REJECTED
            round.result = MergeResult(
                success=False,
                message=f"Precommit failed: {len(precommit_addresses)} precommits "
                        f"(need {validator_network.validator_set.get_quorum_size()})",
                conflicts=[],
            )

        return round

    def commit_phase(
        self,
        round: ConsensusRound,
        branch_manager: "BranchManager",  # noqa: F821
    ) -> ConsensusRound:
        """Execute the merge after successful consensus.

        Args:
            round: The current consensus round (must be COMMIT status)
            branch_manager: BranchManager to execute the merge

        Returns:
            Updated ConsensusRound with result
        """
        round.status = ConsensusStatus.COMMIT

        result = branch_manager.merge_branch(
            source=round.proposal.branch_name,
            strategy=ResolutionStrategy.PREFER_SOURCE,
        )

        round.result = result
        if not result.success:
            # Merge failed, but consensus was achieved — unusual case
            pass

        return round

    def run_consensus(
        self,
        branch_state: "BranchState",
        branch_name: str,
        proposer: str,
        branch_manager: "BranchManager",
        main_state: "BranchState | None" = None,
        validate_fn: Callable | None = None,
        precommit_fn: Callable | None = None,
    ) -> ConsensusRound:
        """Run full consensus round: PROPOSE → PREVOTE → PRECOMMIT → COMMIT.

        Args:
            branch_state: State of the branch to merge
            branch_name: Name of the branch
            proposer: Validator address proposing the merge
            branch_manager: BranchManager to commit the merge
            main_state: Main branch state (for validation)
            validate_fn: Custom validation function
            precommit_fn: Custom precommit function

        Returns:
            Final ConsensusRound with result
        """
        if main_state is None:
            main_state = branch_manager.get_main_state()

        # PROPOSE
        round = self.propose(branch_state, branch_name, proposer)

        # PREVOTE
        round = self.prevote_phase(
            round, self.validator_network,
            validate_fn=validate_fn,
            branch_state=branch_state,
            main_state=main_state,
        )

        if round.status == ConsensusStatus.REJECTED:
            return round

        # PRECOMMIT
        round = self.precommit_phase(
            round, self.validator_network,
            precommit_fn=precommit_fn,
        )

        if round.status == ConsensusStatus.REJECTED:
            return round

        # COMMIT
        round = self.commit_phase(round, branch_manager)

        return round
