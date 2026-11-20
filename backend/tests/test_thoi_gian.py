import unittest
from datetime import datetime, timezone
from unittest.mock import patch
from zoneinfo import ZoneInfo

from app.core import thoi_gian
from app.core.config import Settings


class ThoiGianTests(unittest.TestCase):
    def test_bay_gio_theo_mui_gio_he_thong_khong_kem_tzinfo(self):
        luc = thoi_gian.bay_gio()
        self.assertIsNone(luc.tzinfo)
        utc = datetime.now(timezone.utc).replace(tzinfo=None)
        lech = (luc - utc).total_seconds() / 3600
        self.assertAlmostEqual(lech, datetime.now(thoi_gian.MUI_GIO).utcoffset().total_seconds() / 3600, delta=0.01)

    def test_mac_dinh_gio_viet_nam(self):
        with patch.dict("os.environ", {}, clear=True):
            self.assertEqual(Settings(_env_file=None).timezone, "Asia/Ho_Chi_Minh")

    def test_mui_gio_sai_bao_loi(self):
        with self.assertRaises(ValueError):
            Settings(_env_file=None, timezone="Sao/Hoa")

    def test_offset_mysql_va_tu_timestamp(self):
        with patch.object(thoi_gian, "MUI_GIO", ZoneInfo("Asia/Ho_Chi_Minh")):
            self.assertEqual(thoi_gian.offset_mysql(), "+07:00")
            moc = datetime(2026, 1, 1, tzinfo=timezone.utc).timestamp()
            self.assertEqual(thoi_gian.tu_timestamp(moc), datetime(2026, 1, 1, 7))
            self.assertEqual(thoi_gian.gan_mui_gio(datetime(2026, 1, 1, 7)).astimezone(timezone.utc).hour, 0)


if __name__ == "__main__":
    unittest.main()
