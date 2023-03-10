from custard.core.factory import MsHelper

single_dict = {"code": "200", "error": "", "message": "", "data": []}
single_mixture = {"code": 200, "details": [{"a1": True, "a2": True}], "total_count": {"c1": 1, "c2": 5}}
double_mixture = {"code": 200, "details": [{"a1": True, "a2": True}, {"b1": True, "b2": True}], "total_count": {"c1": 1, "c2": 5}}
# sd_ov = MsHelper.ov_init(single_dict)
# sm_ov = MsHelper.ov_init(single_mixture)
# dm_ov = MsHelper.ov_init(double_mixture)
oneself_ov = MsHelper.ov_init(double_mixture, oneself=True)
print(oneself_ov)