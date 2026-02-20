"""History page — browse, filter, and compare past compliance scans."""

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import altair as alt
from components import render_comparison_view, render_history_export
from database.operations import get_all_scans, get_scan_by_url
from logger_config import get_logger

logger = get_logger(__name__)

# ── Period map ────────────────────────────────────────────────────────────────
_PERIODS = {
    "Last 7 days":  7,
    "Last 30 days": 30,
    "Last 90 days": 90,
    "All time":     36500,
}


def render_history_page():
    """Render the scan history page."""
    st.markdown("""
    <div class="section-eyebrow">History</div>
    <div class="section-heading">Scan History</div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["  All Scans  ", "  Compare  ", "  Statistics  ", "  Export  "])

    with tab1:
        render_all_scans_view()
    with tab2:
        render_comparison_view_tab()
    with tab3:
        render_statistics_view()
    with tab4:
        render_export_view()


def render_all_scans_view():
    """All scans with filter bar."""
    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    # ── Filter bar ────────────────────────────────────────────────
    f1, f2, f3 = st.columns([2, 2, 3], gap="medium")

    with f1:
        st.caption("GRADE")
        filter_grade = st.multiselect(
            "Grade",
            options=["A", "B", "C", "D", "F"],
            placeholder="All grades",
            label_visibility="collapsed",
            key="filter_grade",
        )

    with f2:
        st.caption("TIME PERIOD")
        period_label = st.radio(
            "Period",
            options=list(_PERIODS.keys()),
            index=1,
            horizontal=True,
            label_visibility="collapsed",
            key="period_filter",
        )
        date_range = _PERIODS[period_label]

    with f3:
        st.caption("SEARCH URL")
        search_url = st.text_input(
            "Search URL",
            placeholder="Filter by domain — e.g. example.com",
            label_visibility="collapsed",
            key="search_url",
        )

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # ── Load & filter data ────────────────────────────────────────
    try:
        scans = get_scan_by_url(search_url) if search_url else get_all_scans()

        if not scans:
            st.info("No scans yet — start with a Quick Scan or Batch Scan.")
            return

        df = pd.DataFrame(scans)

        if filter_grade:
            df = df[df["grade"].isin(filter_grade)]

        if "scan_date" in df.columns:
            cutoff = datetime.now() - timedelta(days=date_range)
            df["scan_date"] = pd.to_datetime(df["scan_date"])
            df = df[df["scan_date"] >= cutoff]

        if df.empty:
            st.info("No scans match the current filters.")
            return

        # ── Summary metrics ───────────────────────────────────────
        total = len(df)
        avg_score = df["score"].mean() if "score" in df.columns else 0
        compliant = int((df["score"] >= 80).sum()) if "score" in df.columns else 0
        at_risk = int((df["score"] < 60).sum()) if "score" in df.columns else 0

        m1, m2, m3, m4 = st.columns(4, gap="medium")
        with m1:
            st.metric("Total Scans", total)
        with m2:
            st.metric("Avg Score", f"{avg_score:.1f}")
        with m3:
            st.metric("Compliant (≥80)", compliant)
        with m4:
            st.metric("At Risk (<60)", at_risk)

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

        # ── Scans table ───────────────────────────────────────────
        display_cols = [c for c in ["url", "score", "grade", "status", "scan_date"] if c in df.columns]
        sort_col = "scan_date" if "scan_date" in df.columns else "score"

        st.dataframe(
            df[display_cols].sort_values(sort_col, ascending=False).reset_index(drop=True),
            use_container_width=True,
            hide_index=True,
        )

    except Exception as e:
        logger.error(f"Error loading scan history: {e}")
        st.error("Could not load scan history. Please try again.")


def render_comparison_view_tab():
    """Compare two scans side-by-side."""
    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    try:
        scans = get_all_scans()

        if len(scans) < 2:
            st.info("You need at least 2 scans to compare. Run a few scans first.")
            return

        scan_options = [f"{s['url']}  ·  {s['scan_date']}" for s in scans]

        c1, c2 = st.columns(2, gap="medium")
        with c1:
            st.caption("FIRST SCAN")
            scan1_idx = st.selectbox(
                "First", range(len(scan_options)),
                format_func=lambda i: scan_options[i],
                label_visibility="collapsed", key="comp1",
            )
        with c2:
            st.caption("SECOND SCAN")
            scan2_idx = st.selectbox(
                "Second", range(len(scan_options)),
                format_func=lambda i: scan_options[i],
                label_visibility="collapsed", key="comp2",
            )

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        if scan1_idx == scan2_idx:
            st.warning("Select two different scans to compare.")
        else:
            if st.button("Compare Scans", type="primary", use_container_width=False):
                render_comparison_view(scans[scan1_idx], scans[scan2_idx])

    except Exception as e:
        logger.error(f"Error rendering comparison: {e}")
        st.error("Could not load scans for comparison.")


def render_statistics_view():
    """Statistics and trends for all scans."""
    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    try:
        scans = get_all_scans()

        if not scans:
            st.info("No scan data available yet.")
            return

        df = pd.DataFrame(scans)

        # ── Score distribution ────────────────────────────────────
        if "score" in df.columns:
            st.caption("SCORE DISTRIBUTION")
            score_hist = (
                alt.Chart(df)
                .transform_bin("score_bin", "score", bin=alt.Bin(maxbins=20))
                .transform_aggregate(count="count()", groupby=["score_bin"])
                .mark_bar(color="#58a6ff", cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
                .encode(
                    x=alt.X("score_bin:Q", title="Score", axis=alt.Axis(labelColor="#8b949e", titleColor="#8b949e")),
                    y=alt.Y("count:Q", title="Sites", axis=alt.Axis(labelColor="#8b949e", titleColor="#8b949e")),
                    tooltip=["score_bin:Q", "count:Q"],
                )
                .properties(height=220)
                .configure_view(stroke="transparent", fill="transparent")
                .configure_axis(gridColor="#21262d", domainColor="#21262d")
            )
            st.altair_chart(score_hist, use_container_width=True)

        # ── Grade distribution ────────────────────────────────────
        if "grade" in df.columns:
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            st.caption("GRADE BREAKDOWN")
            grade_df = df["grade"].value_counts().reset_index()
            grade_df.columns = ["Grade", "Count"]
            grade_order = ["A", "B", "C", "D", "F"]
            color_map = {"A": "#3fb950", "B": "#58a6ff", "C": "#d29922", "D": "#f0883e", "F": "#f85149"}

            grade_chart = (
                alt.Chart(grade_df)
                .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
                .encode(
                    x=alt.X("Grade:N", sort=grade_order, axis=alt.Axis(labelColor="#8b949e", title=None)),
                    y=alt.Y("Count:Q", axis=alt.Axis(labelColor="#8b949e", gridColor="#21262d", title="Sites")),
                    color=alt.Color(
                        "Grade:N",
                        scale=alt.Scale(domain=grade_order, range=[color_map[g] for g in grade_order]),
                        legend=None,
                    ),
                    tooltip=["Grade:N", "Count:Q"],
                )
                .properties(height=200)
                .configure_view(stroke="transparent", fill="transparent")
                .configure_axis(gridColor="#21262d", domainColor="#21262d")
            )
            st.altair_chart(grade_chart, use_container_width=True)

        # ── Compliance summary ────────────────────────────────────
        if "score" in df.columns:
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            st.caption("COMPLIANCE STATUS")
            compliant  = int((df["score"] >= 80).sum())
            needs_work = int(((df["score"] >= 60) & (df["score"] < 80)).sum())
            at_risk    = int((df["score"] <  60).sum())
            c1, c2, c3 = st.columns(3, gap="medium")
            with c1:
                st.metric("✅ Compliant", compliant, help="Score ≥ 80")
            with c2:
                st.metric("⚠️ Needs Work", needs_work, help="Score 60–79")
            with c3:
                st.metric("🔴 At Risk", at_risk, help="Score < 60")

    except Exception as e:
        logger.error(f"Error rendering statistics: {e}")
        st.error("Could not load statistics.")


def render_export_view():
    """Export scan data."""
    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    try:
        scans = get_all_scans()
        if not scans:
            st.info("No scans to export yet.")
            return
        render_history_export(scans)
    except Exception as e:
        logger.error(f"Error rendering export: {e}")
        st.error("Could not load scans for export.")


def main():
    if "page" not in st.session_state:
        st.session_state.page = "history"
    render_history_page()


if __name__ == "__main__":
    main()
