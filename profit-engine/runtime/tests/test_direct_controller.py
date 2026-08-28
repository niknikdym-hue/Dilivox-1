import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from profit_engine_runtime.day10_public import (
    GovernorDecision, GovernorState, ProposalKind, build_action_proposal,
)
from profit_engine_runtime.direct_controller import *


NOW = datetime(2026, 8, 28, 12, tzinfo=timezone.utc)


class ControllerFixtures(unittest.TestCase):
    def setUp(self):
        self.registry = ProviderIdentityRegistry()
        self.target = ProviderTarget("target-fixture-1", "dilivox", "yandex_direct",
            "advertiser-fixture", "campaign", "entity-fixture-101")
        self.registry.register(self.target)
        self.locks = ExecutionLockRegistry()

    def proposal(self, proposed="110.00", current="100.00"):
        return build_action_proposal(proposal_id="proposal-fixture", site_id="dilivox",
            kind=ProposalKind.SCALE, target_refs={"provider_target":self.target.target_ref},
            strategy_evidence_digest="a"*64, measurement_refs=("measurement-fixture",),
            provenance_refs=("provenance-fixture",), current_weekly_budget=current,
            proposed_weekly_budget=proposed, private_decision_ref="private-fixture",
            private_decision_digest="b"*64, audit_metadata={"fixture":"true"})

    def governor(self, proposal, increase=None):
        if increase is None:
            current=Decimal(proposal.current_weekly_budget)
            increase=((Decimal(proposal.proposed_weekly_budget)-current)/current)*Decimal("100")
        return bind_governor(proposal, GovernorDecision(
            GovernorState.GOVERNOR_READY_FOR_DAY11_CONTROLLER, (), increase))

    def preflight(self, *, fetched=NOW, state="ACTIVE"):
        return build_preflight(target=self.target, normalized_state=state, status="ACCEPTED",
            current_provider_daily_budget=Decimal("20.00"), currency="RUB",
            strategy_subtype="fixture-strategy", fetched_at=fetched, ttl=timedelta(minutes=5),
            source_ref="raw-fixture", request_id="request-fixture", units=1)

    def budget(self, proposal, governor, preflight, owner=None, daily=None, days=(1,2,3,4,5)):
        return build_budget_plan(proposal=proposal, governor=governor, preflight=preflight,
            proposed_daily=daily or Decimal(proposal.proposed_weekly_budget)/len(days),
            active_days=days, active_day_basis_ref="schedule-fixture-v1", owner_approval=owner)

    def approval(self, proposal, amount=None, **changes):
        values={"approval_id":"approval-fixture","proposal_digest":proposal.proposal_digest,
            "site_id":"dilivox","target_ref":self.target.target_ref,
            "action_kind":"campaign.update_budget",
            "approved_weekly_budget":amount or Decimal(proposal.proposed_weekly_budget),
            "currency":"RUB","approved_at":NOW.isoformat(),
            "expires_at":(NOW+timedelta(hours=1)).isoformat(),"superseded":False,
            "authority_ref":"owner-authority-fixture"}
        values.update(changes); return build_owner_approval(**values)

    def plan(self, proposed="110.00", **changes):
        proposal=changes.pop("proposal",self.proposal(proposed)); governor=changes.pop("governor",self.governor(proposal))
        preflight=changes.pop("preflight",self.preflight()); owner=changes.pop("owner_approval",None)
        budget=changes.pop("budget_plan",None)
        if budget is None and changes.get("method","campaign.update_budget") == "campaign.update_budget":
            budget=self.budget(proposal,governor,preflight,owner)
        cadence=changes.pop("cadence",MutationCadenceEvidence(self.target.target_ref,"2026-08-28",0,"audit-fixture"))
        defaults=dict(proposal=proposal,governor=governor,registry=self.registry,
            target_ref=self.target.target_ref,preflight=preflight,method="campaign.update_budget",
            request_objects=({"entity_ref":self.target.target_ref},),now=NOW,budget_plan=budget,
            owner_approval=owner,cadence=cadence,locks=self.locks)
        defaults.update(changes); return build_controller_plan(**defaults)


class TestAuthorization(ControllerFixtures):
    def test_clean_10_and_exact_20_are_ready_without_extra_approval(self):
        self.assertEqual(ControllerState.READY_FOR_DAY12_EXECUTION,self.plan("110.00")[0].state)
        self.assertEqual(ControllerState.READY_FOR_DAY12_EXECUTION,self.plan("120.00")[0].state)

    def test_20_01_requires_exact_approval(self):
        proposal=self.proposal("120.01"); governor=self.governor(proposal,Decimal("20.01")); pre=self.preflight()
        budget=self.budget(proposal,governor,pre)
        plan,_=self.plan(proposal=proposal,governor=governor,preflight=pre,budget_plan=budget)
        self.assertEqual(ControllerState.BLOCKED_OWNER_APPROVAL,plan.state)
        for approval in (self.approval(proposal,Decimal("120.00")),
                         self.approval(proposal,target_ref="wrong"),
                         self.approval(proposal,expires_at=(NOW-timedelta(seconds=1)).isoformat()),
                         self.approval(proposal,superseded=True)):
            wrong_budget=self.budget(proposal,governor,pre,approval)
            self.assertEqual(ControllerState.BLOCKED_OWNER_APPROVAL,
                self.plan(proposal=proposal,governor=governor,preflight=pre,
                          owner_approval=approval,budget_plan=wrong_budget)[0].state)
        approval=self.approval(proposal); budget=self.budget(proposal,governor,pre,approval)
        self.assertEqual(ControllerState.READY_FOR_DAY12_EXECUTION,
            self.plan(proposal=proposal,governor=governor,preflight=pre,
                      owner_approval=approval,budget_plan=budget)[0].state)

    def test_governor_mismatch_pending_and_forged_proposal_block(self):
        proposal=self.proposal(); other=self.proposal("115")
        self.assertEqual(ControllerState.BLOCKED_GOVERNOR_NOT_READY,
            self.plan(proposal=proposal,governor=self.governor(other))[0].state)
        pending=bind_governor(proposal,GovernorDecision(GovernorState.PENDING_OWNER_APPROVAL,(),Decimal("10")))
        self.assertEqual(ControllerState.BLOCKED_GOVERNOR_NOT_READY,self.plan(proposal=proposal,governor=pending)[0].state)
        forged=replace(proposal,proposal_digest="0"*64)
        self.assertEqual(ControllerState.BLOCKED_GOVERNOR_NOT_READY,self.plan(proposal=forged,governor=self.governor(forged))[0].state)

    def test_exact_identity_only(self):
        self.assertEqual(ControllerState.CONTROLLER_PLAN_INVALID,self.plan(target_ref="campaign name guess")[0].state)

    def test_stale_mismatch_and_dq_preflight_block(self):
        self.assertEqual(ControllerState.BLOCKED_STALE_PROVIDER_STATE,
            self.plan(preflight=self.preflight(fetched=NOW-timedelta(hours=1)))[0].state)
        held=build_preflight(target=self.target,normalized_state="ACTIVE",status="ACCEPTED",
            current_provider_daily_budget=Decimal("20"),currency="RUB",strategy_subtype="fixture",
            fetched_at=NOW,ttl=timedelta(minutes=5),source_ref="raw",dq_holds=("source_hold",))
        self.assertEqual(ControllerState.BLOCKED_STALE_PROVIDER_STATE,self.plan(preflight=held)[0].state)

    def test_allowlist_entity_and_one_object_rule(self):
        self.assertEqual(ControllerState.BLOCKED_PROVIDER_CAPABILITY,self.plan(method="campaign.add")[0].state)
        self.assertEqual(ControllerState.BLOCKED_PROVIDER_CAPABILITY,self.plan(request_objects=())[0].state)
        self.assertEqual(ControllerState.BLOCKED_PROVIDER_CAPABILITY,
            self.plan(request_objects=({"a":1},{"a":2}))[0].state)
        secret="abcdefghijklmnop"
        plan,_=self.plan(request_objects=({"authorization":"Bearer "+secret},))
        self.assertEqual(ControllerState.CONTROLLER_PLAN_INVALID,plan.state)
        self.assertNotIn(secret,str(plan))

    def test_explicit_budget_mapping_seven_and_reduced_schedule(self):
        p=self.proposal("140","100"); g=self.governor(p,Decimal("40"))
        pre=build_preflight(target=self.target,normalized_state="ACTIVE",status="ACCEPTED",
            current_provider_daily_budget=Decimal("100")/Decimal("7"),currency="RUB",
            strategy_subtype="fixture",fetched_at=NOW,ttl=timedelta(minutes=5),source_ref="raw")
        owner=self.approval(p); seven=self.budget(p,g,pre,owner,daily=Decimal("20"),days=(1,2,3,4,5,6,7))
        self.assertEqual(140_000_000,seven.provider_integer_micros*7)
        pre=self.preflight()
        reduced=self.budget(self.proposal("110"),self.governor(self.proposal("110")),pre,
            daily=Decimal("22"),days=(1,2,3,4,5))
        self.assertEqual((1,2,3,4,5),reduced.active_days)
        with self.assertRaises(ValueError): self.budget(p,g,pre,owner,daily=Decimal("20"),days=())
        with self.assertRaises(ValueError): self.budget(p,g,pre,owner,daily=Decimal("19"),days=(1,2,3,4,5,6,7))

    def test_cadence_kills_and_lock(self):
        cadence=MutationCadenceEvidence(self.target.target_ref,"2026-08-28",1,"audit")
        self.assertEqual(ControllerState.BLOCKED_MUTATION_CADENCE,self.plan(cadence=cadence)[0].state)
        refs={"global":"profit-engine","site":"dilivox","provider":"yandex_direct",
              "advertiser":"advertiser-fixture","target":self.target.target_ref,
              "experiment":"proposal-fixture"}
        for scope in ("global","site","provider","advertiser","target","experiment"):
            self.assertEqual(ControllerState.BLOCKED_KILL_SWITCH,
                self.plan(kill_switches=(KillSwitch(scope,refs[scope],True),))[0].state)
        self.assertEqual(ControllerState.READY_FOR_DAY12_EXECUTION,
            self.plan(kill_switches=(KillSwitch("target","unrelated",True),))[0].state)
        self.assertTrue(self.locks.acquire(self.target.lock_key,NOW,timedelta(minutes=2)))
        self.assertEqual(ControllerState.BLOCKED_EXECUTION_LOCK,self.plan()[0].state)
        other=ProviderTarget("target-2","dilivox","yandex_direct","advertiser-fixture","campaign","entity-2")
        self.assertFalse(self.locks.is_locked(other.lock_key,NOW))


class TestSimulationAndAudit(ControllerFixtures):
    def test_success_requires_exact_readback(self):
        plan,audit=self.plan(); expected={"daily_budget":Decimal("22")}
        tx=InMemoryDirectTransport(FakeResponse("RESPONSE",200,object_state="SUCCESS",request_id="req",units=2),expected)
        result=simulate_with_fake(plan,tx,expected,{"daily_budget":Decimal("20")},audit,NOW)
        self.assertEqual("SYNTHETIC_COMPLETED",result.state); self.assertEqual((1,1),(tx.dispatch_count,tx.read_count)); self.assertTrue(audit.valid())

    def test_http_200_object_failure_is_not_success(self):
        plan,audit=self.plan(); expected={"daily_budget":Decimal("22")}
        tx=InMemoryDirectTransport(FakeResponse("RESPONSE",200,object_state="ERROR"),expected)
        self.assertEqual("EXECUTION_UNCERTAIN_REVIEW",simulate_with_fake(plan,tx,expected,{},audit,NOW).state)

    def test_timeout_never_blind_retries(self):
        plan,audit=self.plan(); desired={"daily_budget":Decimal("22")}; before={"daily_budget":Decimal("20")}
        tx=InMemoryDirectTransport(FakeResponse("TIMEOUT",None,request_id="req-timeout"),desired)
        self.assertEqual("RECOVERED_APPLIED",simulate_with_fake(plan,tx,desired,before,audit,NOW).state)
        self.assertEqual(1,tx.dispatch_count)
        plan,audit=self.plan(); tx=InMemoryDirectTransport(FakeResponse("TIMEOUT",None),before)
        self.assertEqual("EXPLICIT_RETRY_PLAN_REQUIRED",simulate_with_fake(plan,tx,desired,before,audit,NOW).state)
        self.assertEqual(1,tx.dispatch_count)
        plan,audit=self.plan(); tx=InMemoryDirectTransport(FakeResponse("TIMEOUT",None),{"daily_budget":Decimal("21")})
        self.assertEqual("EXECUTION_UNCERTAIN_REVIEW",simulate_with_fake(plan,tx,desired,before,audit,NOW).state)

    def test_rollback_only_from_exact_preflight(self):
        pre=self.preflight(); rollback=derive_rollback("campaign.update_budget",pre)
        self.assertEqual(Decimal("20"),rollback.desired_state["daily_budget"]); self.assertFalse(rollback.executable)
        unknown=replace(pre,current_provider_daily_budget=None)
        self.assertIsNone(derive_rollback("campaign.update_budget",unknown).method)

    def test_toctou_requires_same_fresh_normalized_state(self):
        expected=self.preflight(); fresh=self.preflight()
        self.assertTrue(pre_dispatch_snapshot_matches(expected,fresh,NOW))
        self.assertFalse(pre_dispatch_snapshot_matches(expected,self.preflight(state="SUSPENDED"),NOW))
        self.assertFalse(pre_dispatch_snapshot_matches(expected,self.preflight(fetched=NOW-timedelta(hours=1)),NOW))

    def test_audit_tamper_and_redaction(self):
        chain=AuditChain(); chain.append("PLAN_CREATED",NOW,{"Authorization":"OAuth abcdefghijklmnop","note":"Bearer abcdefghijklmnop"},("abcdefghijklmnop",))
        self.assertTrue(chain.valid()); self.assertNotIn("abcdefghijklmnop",str(chain.records))
        record=chain.records[0]; chain.records[0]=replace(record,event="TAMPERED")
        self.assertFalse(chain.valid())

    def test_default_runtime_has_no_real_writer(self):
        self.assertTrue(assert_no_real_writer_reachable())
        self.assertEqual(0,REAL_PROVIDER_REQUESTS); self.assertEqual(0,ADVERTISING_SPEND)
        self.assertFalse(PRODUCTION_WRITER_ENABLED)
        self.assertNotIn("EXECUTED",{state.value for state in ControllerState})


if __name__ == "__main__": unittest.main()
