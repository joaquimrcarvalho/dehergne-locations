"""
Tests for timelink
"""
import timelink

class TestTimelinkTopLevel:

    def test_get_mhk_env(self):
        mhk_env = timelink.get_mhk_env()
        print(mhk_env)
        assert len(mhk_env)>0, "Could not get any values from ~/.mhk"
