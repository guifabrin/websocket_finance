"""
public static function getListYear($fromDate)
    {
        $years = [];
        $nowYear = date('Y');
        $yearDiff = ($nowYear - $fromDate);
        $j = 10 - $yearDiff;
        if ($j <= 0) {
            $j = 1;
        }
        for ($i = $fromDate - $j; $i <= $fromDate; $i++) {
            $years[] = $i;
        }
        if ($fromDate < $nowYear) {
            for ($i = $fromDate + 1; $i <= $nowYear; $i++) {
                $years[] = $i;
            }
        }
        return $years;
    }

    public static function getYearPeriods($year)
    {
        $arrDtInit = [];
        $arrDtEnd = [];
        for ($i = 0; $i < 12; $i++) {
            $arrDtInit[$i] = date("Y-m-d 00:00:00", strtotime(date($year . '-' . ($i + 1) . '-1')));
            $arrDtEnd[$i] = date('Y-m-t 23:59:00', strtotime($arrDtInit[$i]));
        }
        return (object)['init' => $arrDtInit, 'end' => $arrDtEnd];
    }
"""
import datetime
from calendar import monthrange


def last_day_of_month(date_value):
    return date_value.replace(day=monthrange(date_value.year, date_value.month)[1])


def get_year_periods(year):
    init = []
    end = []
    for month in range(12):
        dt_init = datetime.datetime(year, month + 1, 1, 0, 0, 0)
        init.append(dt_init)
        end.append(last_day_of_month(dt_init))
    return init, end
