from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

DATA_PATH = Path(__file__).parent / 'data' / 'processed' / 'clean_cafe_sales.parquet'

COLORS = {'dark': '#3E2415', 'mid': '#A9744F', 'accent': '#E08A2E', 'soft': '#D9C3A5'}
CHANNEL_COLORS = alt.Scale(domain=['In-store', 'Takeaway'], range=[COLORS['dark'], COLORS['accent']])

NOT_SPECIFIED = 'Not Specified'
MONTHS = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
QUARTERS = ['T1', 'T2', 'T3', 'T4']

WEEKDAY_PT = {
    'Monday': 'Seg', 'Tuesday': 'Ter', 'Wednesday': 'Qua', 'Thursday': 'Qui',
    'Friday': 'Sex', 'Saturday': 'Sáb', 'Sunday': 'Dom',
}

WEEKDAYS = list(WEEKDAY_PT.values())

METRICS = {
    'Faturamento': ('revenue', '$,.0f'),
    'Vendas': ('sales', ',d'),
    'Ticket médio': ('ticket', '$,.2f'),
}

st.set_page_config(page_title='Cafe Sales', page_icon='☕', layout='wide')

st.markdown(
    f"""
    <style>
    .hero {{
        background: linear-gradient(120deg, {COLORS['dark']}, {COLORS['mid']});
        padding: 1.5rem 2rem; border-radius: 18px; margin-bottom: 1rem;
    }}
    .hero h1 {{ color: #fff; margin: 0; font-size: 2rem; padding: 0; }}
    .hero p {{ color: #F3E6D6; margin: .35rem 0 0; }}
    [data-testid="stMetric"] {{ border-radius: 14px; background: rgba(224,138,46,.07); }}
    button[data-baseweb="tab"] {{ font-weight: 600; }}
    </style>
    <div class="hero">
        <h1>☕ Recuperação da Confiabilidade dos Dados de Vendas</h1>
        <p>Análise de vendas de uma cafeteria em 2023, sobre a base limpa e auditável.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

@st.cache_data
def load_sales() -> pd.DataFrame:
    df = pd.read_parquet(DATA_PATH)
    df['total_spent'] = df['total_spent'].astype(float)
    df['price_per_unit'] = df['price_per_unit'].astype(float)
    df['quantity'] = df['quantity'].astype(int)
    for col in ['item', 'payment_method', 'location']:
        df[col] = df[col].astype(str)
    df['month_label'] = df['month'].map(lambda m: MONTHS[int(m) - 1] if pd.notna(m) else None)
    df['quarter_label'] = df['quarter'].map(lambda q: f'T{int(q)}' if pd.notna(q) else None)
    df['weekday_label'] = df['weekday'].map(WEEKDAY_PT)
    return df


def apply_filter(df: pd.DataFrame, column: str, selected: list, options: list) -> pd.DataFrame:
    if not selected or set(selected) == set(options):
        return df
    return df[df[column].isin(selected)]


def agg(df: pd.DataFrame, by) -> pd.DataFrame:
    g = df.groupby(by).agg(
        revenue=('total_spent', 'sum'),
        sales=('transaction_id', 'count'),
        units=('quantity', 'sum'),
    ).reset_index()
    g['ticket'] = g['revenue'] / g['sales']
    return g

def bar(data, x, y, order=None, fmt='$,.0f', ytitle='', horizontal=False, extra=None, height=320):
    d = data.copy()
    d['_top'] = d[y] == d[y].max()
    color = alt.condition('datum._top', alt.value(COLORS['accent']), alt.value(COLORS['mid']))
    tooltip = [x, alt.Tooltip(y, format=fmt, title=ytitle or y), *(extra or [])]

    if horizontal:
        base = alt.Chart(d).encode(
            y=alt.Y(x, sort=order, title=None), x=alt.X(y, title=ytitle)
        )
        text = base.mark_text(align='left', dx=4).encode(text=alt.Text(y, format=fmt))

    else:
        base = alt.Chart(d).encode(
            x=alt.X(x, sort=order, title=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y(y, title=ytitle),
        )
        text = base.mark_text(dy=-8).encode(text=alt.Text(y, format=fmt))

    bars = base.mark_bar(cornerRadius=6).encode(color=color, tooltip=tooltip)
    return (bars + text).properties(height=height).configure_view(strokeWidth=0)


def grouped_bar(data, x, y, group, order=None, fmt='$,.2f', ytitle='', height=320):
    base = alt.Chart(data).encode(
        x=alt.X(x, sort=order, title=None, axis=alt.Axis(labelAngle=0)),
        y=alt.Y(y, title=ytitle),
        xOffset=group,
        color=alt.Color(group, scale=CHANNEL_COLORS, title=None),
    )

    bars = base.mark_bar(cornerRadius=5).encode(
        tooltip=[x, group, alt.Tooltip(y, format=fmt, title=ytitle)]
    )

    return bars.properties(height=height).configure_view(strokeWidth=0)


def money(value: float) -> str:
    return f'${value:,.2f}'


def kpi(col, label, value, delta=None, help=None):
    col.metric(label, value, delta, delta_color='off', border=True, help=help)


def metric_picker(key: str) -> tuple[str, str, str]:
    choice = st.segmented_control('Métrica', list(METRICS), default='Faturamento', key=key)
    choice = choice or 'Faturamento'
    column, fmt = METRICS[choice]
    
    return choice, column, fmt

df = load_sales()

st.sidebar.header('🔎 Filtros')
years = sorted(df['transaction_date'].dt.year.dropna().astype(int).unique())
st.sidebar.selectbox('Ano', years, key='f_year')

st.sidebar.caption('Sem seleção = todos.')
quarter_sel = st.sidebar.pills('Trimestre', QUARTERS, selection_mode='multi', key='f_quarter')
month_sel = st.sidebar.multiselect('Mês', MONTHS, placeholder='Todos', key='f_month')
weekday_sel = st.sidebar.pills('Dia da semana', WEEKDAYS, selection_mode='multi', key='f_weekday')


def reset_filters():
    for key in ('f_quarter', 'f_month', 'f_weekday'):
        st.session_state[key] = []


st.sidebar.button('Limpar filtros', on_click=reset_filters, width='stretch')

f = df
f = apply_filter(f, 'quarter_label', quarter_sel, QUARTERS)
f = apply_filter(f, 'month_label', month_sel, MONTHS)
f = apply_filter(f, 'weekday_label', weekday_sel, WEEKDAYS)

st.sidebar.divider()
st.sidebar.metric('Vendas selecionadas', f'{len(f):,}', f'de {len(df):,} na base', delta_color='off')

date_filter_on = len(f) != len(df) and (quarter_sel or month_sel or weekday_sel)

if date_filter_on:
    st.sidebar.caption(
        f'As {df["transaction_date"].isna().sum()} vendas sem data ficam de fora quando '
        'há filtro de período.'
    )

if f.empty:
    st.warning('Nenhuma venda para essa combinação de filtros. Ajuste ou limpe os filtros.')
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs(
    ['📊 Desempenho geral', '📅 Sazonalidade', '🥐 Produtos e preço', '💳 Canais e pagamento']
)

# 1. Desempenho geral
with tab1:
    revenue, sales = f['total_spent'].sum(), len(f)
    c1, c2, c3, c4 = st.columns(4)
    kpi(c1, 'Faturamento', money(revenue))
    kpi(c2, 'Vendas', f'{sales:,}')
    kpi(c3, 'Ticket médio', money(revenue / sales))
    kpi(c4, 'Unidades por venda', f'{f["quantity"].mean():.2f}')

    quarterly = agg(f, 'quarter_label')
    left, right = st.columns([2, 1])

    with left:
        st.subheader('Faturamento por trimestre')

        if quarterly.empty:
            st.info('Sem vendas com trimestre nessa seleção.')

        else:
            st.altair_chart(
                bar(quarterly, 'quarter_label', 'revenue', QUARTERS, ytitle='Faturamento ($)'),
                width='stretch',
            )
    with right:
        st.subheader('Leitura')

        if len(quarterly) > 1:
            best = quarterly.loc[quarterly['revenue'].idxmax()]
            worst = quarterly.loc[quarterly['revenue'].idxmin()]
            gap = (best['revenue'] - worst['revenue']) / best['revenue']

            st.markdown(
                f"- Melhor: **{best['quarter_label']}**, {money(best['revenue'])}\n"
                f"- Pior: **{worst['quarter_label']}**, {money(worst['revenue'])}\n"
                f"- Diferença entre eles: **{gap:.2%}**"
            )

        undated = f.loc[f['transaction_date'].isna(), 'total_spent'].sum()

        if undated:
            st.caption(f'{money(undated)} vêm de vendas sem data: entram só no total.')

# 2. Sazonalidade
with tab2:
    months, weekdays = agg(f, 'month_label'), agg(f, 'weekday_label')
    c1, c2, c3, c4 = st.columns(4)

    if not months.empty:
        bm, wm = months.loc[months['revenue'].idxmax()], months.loc[months['revenue'].idxmin()]
        kpi(c1, 'Melhor mês', bm['month_label'], money(bm['revenue']))
        kpi(c2, 'Pior mês', wm['month_label'], money(wm['revenue']))

    if not weekdays.empty:
        bd, wd = weekdays.loc[weekdays['revenue'].idxmax()], weekdays.loc[weekdays['revenue'].idxmin()]
        kpi(c3, 'Melhor dia da semana', bd['weekday_label'], money(bd['revenue']))
        kpi(c4, 'Pior dia da semana', wd['weekday_label'], money(wd['revenue']))

    st.subheader('Mês a mês')
    choice, column, fmt = metric_picker('m_month')

    if months.empty:
        st.info('Sem vendas com mês nessa seleção.')

    else:
        st.altair_chart(
            bar(months, 'month_label', column, MONTHS, fmt, choice,
                extra=[alt.Tooltip('sales', title='Vendas', format=',d')]),
            width='stretch',
        )

        st.caption(
            'Fevereiro tem 28 dias: parte da queda dele é calendário. '
            'O que explica os meses fortes e fracos é o número de vendas, não o ticket.'
        )

    st.subheader('Dia da semana')
    split = st.segmented_control('Visão', ['Total', 'Por canal'], default='Total', key='m_split')

    if weekdays.empty:
        st.info('Sem vendas com dia da semana nessa seleção.')

    elif split == 'Por canal':
        by_channel = agg(f[f['location'] != NOT_SPECIFIED], ['weekday_label', 'location'])
        st.altair_chart(
            grouped_bar(by_channel, 'weekday_label', 'revenue', 'location', WEEKDAYS,
                        '$,.0f', 'Faturamento ($)'),
            width='stretch',
        )

        st.caption('Só vendas com canal informado. Cada dia e canal tem cerca de 400 vendas.')

    else:
        st.altair_chart(
            bar(weekdays, 'weekday_label', 'revenue', WEEKDAYS, ytitle='Faturamento ($)'),
            width='stretch',
        )

# 3. Produtos e preço
with tab3:
    known = f[f['item'] != NOT_SPECIFIED]
    items = agg(known, 'item').sort_values('revenue', ascending=False)
    total_rev = f['total_spent'].sum()

    c1, c2, c3, c4 = st.columns(4)

    if not items.empty:
        top = items.iloc[0]
        kpi(c1, 'Item que mais fatura', top['item'], money(top['revenue']))
        top3 = items.head(3)['revenue'].sum() / total_rev
        kpi(c2, 'Top 3 itens', f'{top3:.2%}', 'do faturamento', help=', '.join(items.head(3)['item']))
        most = items.sort_values('units', ascending=False).iloc[0]
        kpi(c3, 'Mais vendido (unidades)', most['item'], f'{most["units"]:,} un.')

    unknown_share = f.loc[f['item'] == NOT_SPECIFIED, 'total_spent'].sum() / total_rev
    kpi(c4, 'Sem item identificado', f'{unknown_share:.2%}', 'do faturamento',
        help='Itens com preço ambíguo ($3,00 ou $4,00) não são recuperados.')

    left, right = st.columns(2)

    with left:
        st.subheader('Itens')
        choice, column, fmt = metric_picker('p_items')

        if items.empty:
            st.info('Sem itens identificados nessa seleção.')

        else:
            order = items.sort_values(column, ascending=False)['item'].tolist()
            st.altair_chart(
                bar(items, 'item', column, order, fmt, choice, horizontal=True, height=360),
                width='stretch',
            )

            st.caption('Preço fixo por item: o faturamento depende mais do preço que do volume.')

    with right:
        st.subheader('Unidades por venda')
        qty = agg(f, 'quantity')
        qty['quantity'] = qty['quantity'].astype(str)
        qty['avg_price'] = qty['revenue'] / qty['units']
        st.altair_chart(
            bar(qty, 'quantity', 'ticket', sorted(qty['quantity']), '$,.2f', 'Ticket médio ($)',
                extra=[alt.Tooltip('sales', title='Vendas', format=',d'),
                       alt.Tooltip('avg_price', title='Preço médio/un.', format='$,.2f')],
                height=360),
            width='stretch',
        )

        st.caption('O ticket cresce com a quantidade, mas o preço médio por unidade fica igual.')

# 4. Canais e pagamento
with tab4:
    with_loc = f[f['location'] != NOT_SPECIFIED]
    with_pay = f[f['payment_method'] != NOT_SPECIFIED]
    loc, pay = agg(with_loc, 'location'), agg(with_pay, 'payment_method')

    def loc_rev(name: str) -> float:
        return loc.loc[loc['location'] == name, 'revenue'].sum()

    instore, takeaway = loc_rev('In-store'), loc_rev('Takeaway')
    c1, c2, c3, c4 = st.columns(4)
    kpi(c1, 'In-store', money(instore),
        f'{instore / takeaway - 1:+.1%} vs Takeaway' if takeaway else None)
    kpi(c2, 'Takeaway', money(takeaway))

    if not pay.empty:
        lead = pay.loc[pay['revenue'].idxmax()]
        kpi(c3, 'Pagamento líder', lead['payment_method'], money(lead['revenue']),
            help='A diferença entre as formas é menor que as vendas sem forma informada.')

    no_pay = (f['payment_method'] == NOT_SPECIFIED).mean()
    kpi(c4, 'Sem pagamento informado', f'{no_pay:.1%}', 'das vendas')

    left, right = st.columns(2)

    with left:
        st.subheader('Canal')

        if loc.empty:
            st.info('Sem vendas com canal nessa seleção.')

        else:
            donut = (
                alt.Chart(loc)
                .mark_arc(innerRadius=70, cornerRadius=4)
                .encode(
                    theta='revenue',
                    color=alt.Color('location', scale=CHANNEL_COLORS, title=None),
                    tooltip=['location', alt.Tooltip('revenue', format='$,.2f', title='Faturamento'),
                             alt.Tooltip('sales', format=',d', title='Vendas'),
                             alt.Tooltip('ticket', format='$,.2f', title='Ticket médio')],
                )
                .properties(height=320)
            )

            st.altair_chart(donut, width='stretch')

        st.caption(f'Compara só as {len(with_loc):,} vendas com canal informado.')

    with right:
        st.subheader('Forma de pagamento')
        choice, column, fmt = metric_picker('c_pay')

        if pay.empty:
            st.info('Sem vendas com forma de pagamento nessa seleção.')

        else:
            st.altair_chart(bar(pay, 'payment_method', column, None, fmt, choice), width='stretch')

    st.subheader('Ticket médio: pagamento × canal')
    both = agg(f[(f['location'] != NOT_SPECIFIED) & (f['payment_method'] != NOT_SPECIFIED)],
               ['payment_method', 'location'])

    if both.empty:
        st.info('Sem vendas com canal e pagamento nessa seleção.')

    else:
        st.altair_chart(
            grouped_bar(both, 'payment_method', 'ticket', 'location', None, '$,.2f', 'Ticket médio ($)'),
            width='stretch',
        )

st.caption('Fonte: data/processed/clean_cafe_sales.parquet · decisões de limpeza em docs/cleaning_decisions.md')