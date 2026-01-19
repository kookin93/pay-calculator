from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP, ROUND_FLOOR

import streamlit as st


APP_DIR = Path(__file__).resolve().parent
LOGO_FILENAME = "로고_검정색.png"

OFFICE_NAME = "인화세무회계컨설팅"
OFFICE_PHONE = "042-222-7208"
OFFICE_ADDRESS = "대전 중구 충무로 173 대현빌딩 6층"

WEEKS_PER_MONTH = Decimal("4.345")  # 엑셀 고정값

# 엑셀 AI19 AJ19 AK19 AL19
PENSION_RATE = Decimal("0.045")
HEALTH_RATE = Decimal("0.03545")
CARE_RATE = Decimal("0.1295")
EMPLOY_RATE = Decimal("0.009")


def d(x) -> Decimal:
    return Decimal(str(x))


def round0(x: Decimal) -> Decimal:
    # 엑셀 ROUND(x,0) 동작을 양수 기준으로 동일하게 맞춤
    return x.quantize(Decimal("1"), rounding=ROUND_HALF_UP)


def floor_to_step(x: Decimal, step: Decimal) -> Decimal:
    # 엑셀 ROUNDDOWN(x, -n) 대응
    # step=1000 이면 천 단위 버림
    # step=10 이면 십 단위 버림
    if step == 0:
        return x
    return (x / step).to_integral_value(rounding=ROUND_FLOOR) * step


def won(x: Decimal) -> str:
    return f"{int(x):,}원"


def compute(
    annual_salary: Decimal,        # Z
    daily_work_hours: Decimal,     # L
    weekly_ot_hours: Decimal,      # P
    work_days_per_week: Decimal,   # M13
    min_wage: Decimal,             # AR6
    min_inclusion_ratio: Decimal,  # AR10
    meal: Decimal,                 # S
    car: Decimal,                  # T
    child: Decimal,                # U
    duty: Decimal,                 # V
    grade: Decimal,                # W
    etc_allow: Decimal,            # X
    etc_deduct: Decimal,           # AM
) -> dict:
    # AR7 = ROUND(AR6*209,0)
    min_monthly_wage = round0(min_wage * Decimal("209"))

    # AR11 = ROUND(AR7*AR10,0)
    min_non_included = round0(min_monthly_wage * min_inclusion_ratio)

    # Y = ROUND(Z/12,0)
    monthly_pay = round0(annual_salary / Decimal("12"))

    # M = ROUND(((L*근로일)+L)*4.345,0)
    monthly_standard_hours = round0(((daily_work_hours * work_days_per_week) + daily_work_hours) * WEEKS_PER_MONTH)

    # Q = P*4.345
    monthly_ot_hours = weekly_ot_hours * WEEKS_PER_MONTH

    # R = M + (P*1.5*4.345)
    weighted_total_hours = monthly_standard_hours + (weekly_ot_hours * Decimal("1.5") * WEEKS_PER_MONTH)

    if weighted_total_hours == 0:
        raise ValueError("시간 값이 0이라 계산할 수 없습니다")

    # AB = Y / R
    hourly = monthly_pay / weighted_total_hours

    # O = ROUND(Q*AB*1.5,0)
    fixed_ot_pay = round0(monthly_ot_hours * hourly * Decimal("1.5"))

    # 수당 합계
    allowances_sum = meal + car + child + duty + grade + etc_allow

    # N = Y - (O + 수당합계)
    base_pay = monthly_pay - (fixed_ot_pay + allowances_sum)

    # AA = CHECK
    check_ok = (monthly_pay == (base_pay + fixed_ot_pay + allowances_sum))

    # AC = 최저임금 비교기준임금
    non_tax_sum = meal + car + child
    if non_tax_sum > 0:
        compare_wage = (base_pay + non_tax_sum - min_non_included) / monthly_standard_hours
    else:
        compare_wage = (base_pay + non_tax_sum) / monthly_standard_hours

    # AD = 준수여부
    compliance = "준수" if compare_wage >= min_wage else "미준수"

    # AF = 과세금액 = Y - (S+T+U)
    taxable = monthly_pay - non_tax_sum

    # AG 소득세는 업로드 엑셀에서 #REF!로 IFERROR 처리되어 0이 됨
    income_tax = Decimal("0")

    # AH = 주민세 = ROUNDDOWN(AG*0.1,-1)
    resident_tax = floor_to_step(income_tax * Decimal("0.1"), Decimal("10"))

    # AI = 국민연금 = ROUNDDOWN(ROUNDDOWN(AF,-3)*0.045,-1)
    pension_base = floor_to_step(taxable, Decimal("1000"))
    pension = floor_to_step(pension_base * PENSION_RATE, Decimal("10"))

    # AJ = 건강보험 = ROUNDDOWN(AF*0.03545,-1)
    health = floor_to_step(taxable * HEALTH_RATE, Decimal("10"))

    # AK = 장기요양 = ROUNDDOWN(AJ*0.1295,-1)
    care = floor_to_step(health * CARE_RATE, Decimal("10"))

    # AL = 고용보험 = ROUNDDOWN(AF*0.009,-1)
    employ = floor_to_step(taxable * EMPLOY_RATE, Decimal("10"))

    # AN = 총 공제금액 = SUM(AG:AM)
    total_deduct = income_tax + resident_tax + pension + health + care + employ + etc_deduct

    # AO = 실지급액 = Y - AN
    net_pay = monthly_pay - total_deduct

    # 검증값
    diff = (base_pay + fixed_ot_pay + allowances_sum) - monthly_pay
    diff_abs = abs(diff)

    return {
        "monthly_pay": monthly_pay,
        "monthly_standard_hours": monthly_standard_hours,
        "monthly_ot_hours": round0(monthly_ot_hours),
        "hourly": round0(hourly),
        "base_pay": round0(base_pay),
        "fixed_ot_pay": fixed_ot_pay,
        "allowances_sum": round0(allowances_sum),
        "check_ok": check_ok,
        "compare_wage": round0(compare_wage),
        "compliance": compliance,
        "min_wage": round0(min_wage),
        "taxable": round0(taxable),
        "income_tax": round0(income_tax),
        "resident_tax": round0(resident_tax),
        "pension": round0(pension),
        "health": round0(health),
        "care": round0(care),
        "employ": round0(employ),
        "etc_deduct": round0(etc_deduct),
        "total_deduct": round0(total_deduct),
        "net_pay": round0(net_pay),
        "diff_abs": round0(diff_abs),
    }


def render_footer() -> None:
    st.markdown(
        f"""
        <style>
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
            z-index: 9999;
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
          .wrap-pad {{
            padding-bottom: 78px;
          }}
        </style>
        <div class="footer">
          <div class="footer-inner">
            <div><strong>{OFFICE_NAME}</strong></div>
            <div>{OFFICE_PHONE}</div>
            <div>{OFFICE_ADDRESS}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


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

    annual_salary_int = st.number_input("상여금 제외 연봉", min_value=0, value=36000000, step=100000, format="%d")

    work_days = st.number_input("주 근로일", min_value=1, value=5, step=1, format="%d")
    daily_hours = st.number_input("1일 근로시간", min_value=0.0, value=8.0, step=0.5)

    weekly_ot = st.number_input("주 고정연장시간", min_value=0.0, value=9.0, step=0.5)

    st.divider()
    st.subheader("최저임금")
    min_wage_int = st.number_input("최저시급", min_value=0, value=10320, step=10, format="%d")
    inclusion_ratio = st.number_input("최저 산입비율", min_value=0.0, max_value=1.0, value=0.0, step=0.01)

    st.divider()
    st.subheader("비과세 수당")
    meal_int = st.number_input("식대", min_value=0, value=0, step=10000, format="%d")
    car_int = st.number_input("차량유지비", min_value=0, value=0, step=10000, format="%d")
    child_int = st.number_input("자녀 양육수당", min_value=0, value=0, step=10000, format="%d")

    st.divider()
    st.subheader("과세 수당")
    duty_int = st.number_input("직책수당", min_value=0, value=0, step=10000, format="%d")
    grade_int = st.number_input("직급수당", min_value=0, value=0, step=10000, format="%d")
    etc_allow_int = st.number_input("기타수당", min_value=0, value=0, step=10000, format="%d")

    st.divider()
    st.subheader("기타 공제")
    etc_deduct_int = st.number_input("기타공제", min_value=0, value=0, step=10000, format="%d")

try:
    r = compute(
        annual_salary=d(annual_salary_int),
        daily_work_hours=d(daily_hours),
        weekly_ot_hours=d(weekly_ot),
        work_days_per_week=d(work_days),
        min_wage=d(min_wage_int),
        min_inclusion_ratio=d(inclusion_ratio),
        meal=d(meal_int),
        car=d(car_int),
        child=d(child_int),
        duty=d(duty_int),
        grade=d(grade_int),
        etc_allow=d(etc_allow_int),
        etc_deduct=d(etc_deduct_int),
    )
except Exception as e:
    st.error(str(e))
    st.stop()

st.markdown('<div class="wrap-pad">', unsafe_allow_html=True)

st.subheader("계산 결과")
col1, col2 = st.columns(2)
with col1:
    st.metric("총 월급여액", won(r["monthly_pay"]))
    st.metric("기본급", won(r["base_pay"]))
    st.metric("고정연장수당", won(r["fixed_ot_pay"]))
with col2:
    st.metric("통상시급", won(r["hourly"]))
    st.metric("비과세 수당 합계", won(d(meal_int + car_int + child_int)))
    st.metric("과세금액", won(r["taxable"]))

st.divider()
st.subheader("최저임금")
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("최저시급", won(r["min_wage"]))
with c2:
    st.metric("비교기준임금", won(r["compare_wage"]))
with c3:
    st.metric("준수여부", r["compliance"])

st.divider()
st.subheader("공제와 실지급액")
c1, c2 = st.columns(2)
with c1:
    st.write("소득세")
    st.write(won(r["income_tax"]))
    st.write("주민세")
    st.write(won(r["resident_tax"]))
    st.write("국민연금")
    st.write(won(r["pension"]))
    st.write("건강보험")
    st.write(won(r["health"]))
    st.write("장기요양보험")
    st.write(won(r["care"]))
    st.write("고용보험")
    st.write(won(r["employ"]))
    st.write("기타공제")
    st.write(won(r["etc_deduct"]))
with c2:
    st.metric("총 공제금액", won(r["total_deduct"]))
    st.metric("실지급액", won(r["net_pay"]))
    st.caption("소득세는 업로드 엑셀에서 #REF!로 0 처리되는 상태를 그대로 반영했습니다")

st.divider()
st.subheader("검증")
if r["diff_abs"] <= Decimal("1"):
    st.success(f"정상. 차이 절대값 {int(r['diff_abs']):,}원")
else:
    st.error(f"비정상. 차이 절대값 {int(r['diff_abs']):,}원")

if r["check_ok"]:
    st.caption("CHECK. OK")
else:
    st.caption("CHECK. NOTOK")

render_footer()
st.markdown("</div>", unsafe_allow_html=True)
