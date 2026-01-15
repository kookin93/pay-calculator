from pathlib import Path
from decimal import Decimal
from decimal import ROUND_UP
from decimal import ROUND_HALF_UP

import streamlit as st


APP_DIR = Path(__file__).resolve().parent
LOGO_FILENAME = "로고_검정색.png"

OFFICE_NAME = "인화세무회계컨설팅"
OFFICE_PHONE = "042-222-7208"
OFFICE_ADDRESS = "대전 중구 충무로 173 대현빌딩 6층"


def d(x) -> Decimal:
    return Decimal(str(x))


def roundup_0(x: Decimal) -> Decimal:
    return x.quantize(Decimal("1"), rounding=ROUND_UP)


def round_half_up_0(x: Decimal) -> Decimal:
    return x.quantize(Decimal("1"), rounding=ROUND_HALF_UP)


def format_won(x: Decimal) -> str:
    return f"{int(x):,}원"


def compute(
    annual_salary: Decimal,
    weekly_work_hours: Decimal,
    weekly_ot_hours: Decimal,
    min_wage: Decimal,
    meal_allowance: Decimal,
    car_allowance: Decimal,
) -> dict:
    factor = d("4.345")

    weekly_holiday_hours = weekly_work_hours / d("5")
    weekly_paid_hours = weekly_work_hours + weekly_holiday_hours

    monthly_standard_hours = roundup_0(weekly_paid_hours * factor)
    monthly_ot_hours = roundup_0(weekly_ot_hours * factor)

    monthly_salary = annual_salary / d("12")

    denominator = monthly_standard_hours + (monthly_ot_hours * d("1.5"))
    if denominator == 0:
        raise ValueError("시간 값이 0이어서 계산할 수 없습니다")

    hourly = (monthly_salary - meal_allowance - car_allowance) / denominator

    base_pay = roundup_0(hourly * monthly_standard_hours)
    fixed_ot_pay = roundup_0(hourly * monthly_ot_hours * d("1.5"))
    total_pay = base_pay + fixed_ot_pay + meal_allowance + car_allowance

    diff = total_pay - monthly_salary
    min_wage_result = "최저이상" if hourly >= min_wage else "최저미만"

    return {
        "monthly_salary": monthly_salary,
        "hourly": hourly,
        "base_pay": base_pay,
        "fixed_ot_pay": fixed_ot_pay,
        "total_pay": total_pay,
        "diff": diff,
        "min_wage_result": min_wage_result,
        "meal_allowance": meal_allowance,
        "car_allowance": car_allowance,
    }


def render_payslip_html(result: dict, min_wage: Decimal) -> str:
    hourly_disp = round_half_up_0(result["hourly"])
    min_wage_disp = round_half_up_0(min_wage)

    base_pay_disp = result["base_pay"]
    ot_pay_disp = result["fixed_ot_pay"]
    meal_disp = roundup_0(d(result["meal_allowance"]))
    car_disp = roundup_0(d(result["car_allowance"]))
    total_disp = result["total_pay"]

    html = f"""
    <style>
      .wrap {{
        max-width: 860px;
        margin: 0 auto;
        padding-bottom: 78px;
      }}
      table.payslip {{
        width: 100%;
        border-collapse: collapse;
        margin: 10px 0 18px 0;
        font-size: 15px;
      }}
      table.payslip th {{
        text-align: left;
        padding: 10px 10px;
        border: 1px solid #e6e6e6;
        background: #fafafa;
        font-weight: 700;
      }}
      table.payslip td {{
        padding: 10px 10px;
        border: 1px solid #e6e6e6;
      }}
      td.r {{
        text-align: right;
        white-space: nowrap;
      }}
      .kpi {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
        margin-top: 6px;
        margin-bottom: 12px;
      }}
      .card {{
        border: 1px solid #e6e6e6;
        border-radius: 10px;
        padding: 12px 14px;
        background: white;
      }}
      .card .t {{
        font-size: 13px;
        color: #666;
        margin-bottom: 6px;
      }}
      .card .v {{
        font-size: 20px;
        font-weight: 800;
      }}
      .muted {{
        color: #666;
        font-size: 13px;
      }}
      .footer {{
        position: fixed;
        left: 0;
        right: 0;
        bottom: 0;
        background: #ffffff;
        border-top: 1px solid #e6e6e6;
        padding: 10px 12px;
        font-size: 13px;
        color: #444;
      }}
      .footer-inner {{
        max-width: 860px;
        margin: 0 auto;
        display: flex;
        justify-content: space-between;
        gap: 12px;
        flex-wrap: wrap;
      }}
      .footer strong {{
        font-weight: 700;
      }}
    </style>

    <div class="wrap">
      <div class="kpi">
        <div class="card">
          <div class="t">통상시급</div>
          <div class="v">{format_won(hourly_disp)}</div>
          <div class="muted">표시는 소수 첫째 자리에서 반올림</div>
        </div>
        <div class="card">
          <div class="t">최저시급 기준</div>
          <div class="v">{format_won(min_wage_disp)}</div>
          <div class="muted">{result["min_wage_result"]}</div>
        </div>
      </div>

      <table class="payslip">
        <tr><th colspan="2">급여 구성</th></tr>
        <tr><td>기본급</td><td class="r">{format_won(base_pay_disp)}</td></tr>
        <tr><td>고정연장수당</td><td class="r">{format_won(ot_pay_disp)}</td></tr>
        <tr><td>식대</td><td class="r">{format_won(meal_disp)}</td></tr>
        <tr><td>자가운전보조금</td><td class="r">{format_won(car_disp)}</td></tr>
        <tr><td><b>총급여</b></td><td class="r"><b>{format_won(total_disp)}</b></td></tr>
      </table>
    </div>

    <div class="footer">
      <div class="footer-inner">
        <div><strong>{OFFICE_NAME}</strong></div>
        <div>{OFFICE_PHONE}</div>
        <div>{OFFICE_ADDRESS}</div>
      </div>
    </div>
    """
    return html


st.set_page_config(page_title="급여 계산기", layout="centered")

logo_path = APP_DIR / LOGO_FILENAME
if logo_path.exists():
    st.image(str(logo_path), use_container_width=True)

st.markdown("## 급여 계산기")

st.warning(
    "저작권 안내\n"
    "본 프로그램과 화면 구성 및 산출물은 저작권 보호 대상입니다\n"
    "사전 서면 동의 없이 복제 수정 배포 게시를 금지합니다"
)
st.info(
    "참고 안내\n"
    "본 계산 결과는 참고용입니다\n"
    "법적 자문 또는 확정 금액이 아닙니다\n"
    "최종 판단과 책임은 사용자에게 있습니다"
)

with st.sidebar:
    st.header("입력")

    annual_salary_int = st.number_input(
        "연봉",
        min_value=0,
        value=36000000,
        step=100000,
        format="%d",
    )

    weekly_work_hours_float = st.number_input(
        "주 근로시간",
        min_value=0.0,
        value=40.0,
        step=0.5,
    )

    weekly_ot_hours_float = st.number_input(
        "주 연장시간",
        min_value=0.0,
        value=9.0,
        step=0.5,
    )

    min_wage_int = st.number_input(
        "최저시급",
        min_value=0,
        value=10320,
        step=10,
        format="%d",
    )

    meal_allowance_int = st.number_input(
        "식대",
        min_value=0,
        value=0,
        step=10000,
        format="%d",
    )

    car_allowance_int = st.number_input(
        "자가운전보조금",
        min_value=0,
        value=0,
        step=10000,
        format="%d",
    )

annual_salary = d(annual_salary_int)
weekly_work_hours = d(weekly_work_hours_float)
weekly_ot_hours = d(weekly_ot_hours_float)
min_wage = d(min_wage_int)
meal_allowance = d(meal_allowance_int)
car_allowance = d(car_allowance_int)

try:
    result = compute(
        annual_salary=annual_salary,
        weekly_work_hours=weekly_work_hours,
        weekly_ot_hours=weekly_ot_hours,
        min_wage=min_wage,
        meal_allowance=meal_allowance,
        car_allowance=car_allowance,
    )
except Exception as e:
    st.error(str(e))
    st.stop()

st.subheader("계산 결과")
st.markdown(render_payslip_html(result, min_wage), unsafe_allow_html=True)

st.subheader("요약")
monthly_salary_disp = round_half_up_0(result["monthly_salary"])
total_disp = result["total_pay"]
diff_abs = abs(result["diff"])

status_ok = diff_abs <= d("1")
status_text = "정상" if status_ok else "비정상"
diff_abs_disp = round_half_up_0(diff_abs)

col1, col2 = st.columns(2)
with col1:
    st.metric("월급여 기준", f"{int(monthly_salary_disp):,}원")
with col2:
    st.metric("총급여", f"{int(total_disp):,}원")

if status_ok:
    st.success(f"검증 결과. {status_text}. 차이 절대값 {int(diff_abs_disp):,}원")
else:
    st.error(f"검증 결과. {status_text}. 차이 절대값 {int(diff_abs_disp):,}원")

st.caption("검증 기준은 총급여 minus 월급여 입니다. 차이 절대값이 1원 이하이면 정상입니다")
