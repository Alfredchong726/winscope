import pytest
from src.services.privilege_manager import PrivilegeManager


class TestPrivilegeManager:

    def test_is_admin_check(self):
        pm = PrivilegeManager()

        is_admin = pm.is_admin()
        assert isinstance(is_admin, bool)

    def test_is_admin_cached(self):
        pm = PrivilegeManager()

        result1 = pm.is_admin()
        result2 = pm.is_admin()

        assert result1 == result2

    def test_check_required_privileges(self):
        pm = PrivilegeManager()

        has_priv, msg = pm.check_required_privileges("network")
        assert has_priv is True

        has_priv, msg = pm.check_required_privileges("memory")
        assert isinstance(has_priv, bool)
        assert isinstance(msg, str)

    def test_get_privilege_status_report(self):
        pm = PrivilegeManager()

        report = pm.get_privilege_status_report()

        assert "is_admin" in report
        assert "can_collect_memory" in report
        assert "can_collect_network" in report

        assert report["can_collect_network"] is True

    def test_check_unknown_module(self):
        pm = PrivilegeManager()

        has_priv, msg = pm.check_required_privileges("unknown_module")
        assert has_priv is True
