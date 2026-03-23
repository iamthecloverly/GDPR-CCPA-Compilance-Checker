"""History page — browse, filter, and compare past compliance scans."""

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import altair as alt
from components import render_comparison_view, render_history_export
from database.operations import (
    get_all_scans, get_scan_by_url,
    get_scans_paginated, get_scan_count,
    delete_scans_by_ids,
)
from libs.export import export_batch_results_to_csv, export_batch_results_to_json
from logger_config import get_logger

logger = get_logger(__name__)

# ── Period map ────────────────────────────────────────────────────────────────
_PERIODS = {
    "Last 7 days":  7,
    "Last 30 days": 30,
    "Last 90 days": 90,
    "All time":     36500,
}

_PAGE_SIZE = 20


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
    """All scans with filter bar and server-side pagination."""
    # ── Filter bar ────────────────────────────────────────────────
    f1, f2, f3 = st.columns([2, 2, 3], gap="medium")

    with f1:
        filter_grade = st.multiselect(
            "Grade",
            options=["A", "B", "C", "D", "F"],
            placeholder="All grades",
            key="filter_grade",
        )

    with f2:
        period_label = st.radio(
            "Time Period",
            options=list(_PERIODS.keys()),
            index=1,
            horizontal=True,
            key="period_filter",
        )

    with f3:
        search_url = st.text_input(
            "Search URL",
            placeholder="Filter by domain — e.g. example.com…",
            key="search_url",
        )

    # Reset page to 1 when any filter changes
    filter_key = (tuple(filter_grade), period_label, search_url)
    if st.session_state.get("_history_filter_key") != filter_key:
        st.session_state["_history_page"] = 1
        st.session_state["_history_filter_key"] = filter_key

    current_page = st.session_state.get("_history_page", 1)
    date_cutoff = datetime.now() - timedelta(days=_PERIODS[period_label])

    # ── DB-level count + paginated fetch ─────────────────────────
    total = get_scan_count(
        url_search=search_url or None,
        grade_filter=filter_grade or None,
        date_cutoff=date_cutoff,
    )

    if total == 0:
        st.markdown("""
<div class="empty-state">
  <div class="empty-state-icon">📭</div>
  <p class="empty-state-title">No scans yet</p>
  <p class="empty-state-body">Run a Quick Scan or Batch Scan to start tracking compliance history.</p>
</div>
""", unsafe_allow_html=True)
        return

    total_pages = max(1, (total + _PAGE_SIZE - 1) // _PAGE_SIZE)
    current_page = min(current_page, total_pages)
    offset = (current_page - 1) * _PAGE_SIZE

    scans = get_scans_paginated(
        offset=offset,
        limit=_PAGE_SIZE,
        url_search=search_url or None,
        grade_filter=filter_grade or None,
        date_cutoff=date_cutoff,
    )

    if not scans:
        st.markdown("""
<div class="empty-state">
  <div class="empty-state-icon">🔍</div>
  <p class="empty-state-title">No matching scans</p>
  <p class="empty-state-body">Try adjusting the grade filter, time period, or URL search.</p>
</div>
""", unsafe_allow_html=True)
        return

    df = pd.DataFrame(scans)

    # ── Summary metrics (aggregate across all matching, not just page) ────
    m1, m2, m3, m4 = st.columns(4, gap="medium")
    with m1:
        st.metric("Total Scans", total)
    with m2:
        avg_score = df["score"].mean() if "score" in df.columns else 0
        st.metric("Avg Score (page)", f"{avg_score:.1f}")
    with m3:
        compliant = int((df["score"] >= 80).sum()) if "score" in df.columns else 0
        st.metric("Compliant (≥80)", compliant)
    with m4:
        at_risk = int((df["score"] < 60).sum()) if "score" in df.columns else 0
        st.metric("At Risk (<60)", at_risk)

    # ── Scans table with row selection ────────────────────────────
    display_cols = [c for c in ["url", "score", "grade", "status", "scan_date"] if c in df.columns]

    if "scan_date" in df.columns:
        df["scan_date"] = pd.to_datetime(df["scan_date"])

    # Prepend a boolean Select column; preserve scan id for actions
    table_df = df[display_cols].copy().reset_index(drop=True)
    table_df.insert(0, "Select", False)
    # Store original scan ids aligned to table rows
    scan_ids = df["id"].tolist() if "id" in df.columns else []

    edited = st.data_editor(
        table_df,
        use_container_width=True,
        hide_index=True,
        column_config={"Select": st.column_config.CheckboxColumn("Select", default=False)},
        disabled=[c for c in table_df.columns if c != "Select"],
        key=f"hist_table_p{current_page}",
    )

    # ── Bulk actions ─────────────────────────────────────────────
    selected_mask = edited["Select"].tolist()
    selected_indices = [i for i, v in enumerate(selected_mask) if v]
    selected_ids = [scan_ids[i] for i in selected_indices if i < len(scan_ids)]
    selected_scans = [scans[i] for i in selected_indices if i < len(scans)]

    if selected_ids:
        st.markdown(f"**{len(selected_ids)} row(s) selected**")
        ba1, ba2, ba3 = st.columns([1, 1, 4])

        with ba1:
            csv_export = export_batch_results_to_csv(selected_scans)
            st.download_button(
                "Export Selected CSV",
                data=csv_export,
                file_name="selected_scans.csv",
                mime="text/csv",
                key="bulk_csv",
            )

        with ba2:
            json_export = export_batch_results_to_json(selected_scans)
            st.download_button(
                "Export Selected JSON",
                data=json_export,
                file_name="selected_scans.json",
                mime="application/json",
                key="bulk_json",
            )

        with ba3:
            if st.session_state.get("_confirm_delete_ids") == selected_ids:
                st.warning(f"Delete {len(selected_ids)} scan(s)? This cannot be undone.")
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("Confirm Delete", type="primary", key="bulk_delete_confirm"):
                        deleted = delete_scans_by_ids(selected_ids)
                        st.session_state.pop("_confirm_delete_ids", None)
                        if deleted:
                            st.toast(f"Deleted {deleted} scan(s).", icon="🗑️")
                            st.session_state["_history_page"] = 1
                            st.rerun()
                        else:
                            st.error("Delete failed — database may not be available.")
                with col_no:
                    if st.button("Cancel", key="bulk_delete_cancel"):
                        st.session_state.pop("_confirm_delete_ids", None)
                        st.rerun()
            else:
                if st.button(
                    f"Delete {len(selected_ids)} selected",
                    type="secondary",
                    key="bulk_delete",
                ):
                    st.session_state["_confirm_delete_ids"] = selected_ids
                    st.rerun()

    # ── Pagination controls ───────────────────────────────────────
    if total_pages > 1:
        st.markdown("")
        pg_left, pg_mid, pg_right = st.columns([1, 2, 1])
        with pg_left:
            if st.button("← Previous", disabled=(current_page <= 1), key="hist_prev"):
                st.session_state["_history_page"] = current_page - 1
                st.rerun()
        with pg_mid:
            st.markdown(
                f"<div style='text-align:center;padding-top:6px;color:#8b949e;'>"
                f"Page {current_page} of {total_pages} &nbsp;·&nbsp; {total} total</div>",
                unsafe_allow_html=True,
            )
        with pg_right:
            if st.button("Next →", disabled=(current_page >= total_pages), key="hist_next"):
                st.session_state["_history_page"] = current_page + 1
                st.rerun()


def render_comparison_view_tab():
    """Compare two scans side-by-side."""
    try:
        scans = get_all_scans()

        if len(scans) < 2:
            st.info("You need at least 2 scans to compare. Run a few scans first.")
            return

        scan_options = [f"{s['url']}  ·  {s['scan_date']}" for s in scans]

        c1, c2 = st.columns(2, gap="medium")
        with c1:
            scan1_idx = st.selectbox(
                "First Scan", range(len(scan_options)),
                format_func=lambda i: scan_options[i],
                key="comp1",
            )
        with c2:
            scan2_idx = st.selectbox(
                "Second Scan", range(len(scan_options)),
                format_func=lambda i: scan_options[i],
                key="comp2",
            )

        if scan1_idx == scan2_idx:
            st.warning("Select two different scans to compare.")
        else:
            if st.button("Compare Scans", type="primary"):
                render_comparison_view(scans[scan1_idx], scans[scan2_idx])

    except Exception as e:
        logger.error(f"Error rendering comparison: {e}")
        st.error("Could not load scans for comparison.")


def render_statistics_view():
    """Statistics and trends for all scans."""
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
                .mark_bar(color="#f59e0b", cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
                .encode(
                    x=alt.X("score_bin:Q", title="Score", axis=alt.Axis(labelColor="#a1a1aa", titleColor="#a1a1aa")),
                    y=alt.Y("count:Q", title="Sites", axis=alt.Axis(labelColor="#a1a1aa", titleColor="#a1a1aa")),
                    tooltip=["score_bin:Q", "count:Q"],
                )
                .properties(height=220)
                .configure_view(stroke="transparent", fill="transparent")
                .configure_axis(gridColor="#27272a", domainColor="#27272a")
            )
            st.altair_chart(score_hist, use_container_width=True)

        # ── Grade distribution ────────────────────────────────────
        if "grade" in df.columns:
            st.caption("GRADE BREAKDOWN")
            grade_df = df["grade"].value_counts().reset_index()
            grade_df.columns = ["Grade", "Count"]
            grade_order = ["A", "B", "C", "D", "F"]
            color_map = {"A": "#3fb950", "B": "#f59e0b", "C": "#d29922", "D": "#f0883e", "F": "#f85149"}

            grade_chart = (
                alt.Chart(grade_df)
                .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
                .encode(
                    x=alt.X("Grade:N", sort=grade_order, axis=alt.Axis(labelColor="#a1a1aa", title=None)),
                    y=alt.Y("Count:Q", axis=alt.Axis(labelColor="#a1a1aa", gridColor="#27272a", title="Sites")),
                    color=alt.Color(
                        "Grade:N",
                        scale=alt.Scale(domain=grade_order, range=[color_map[g] for g in grade_order]),
                        legend=None,
                    ),
                    tooltip=["Grade:N", "Count:Q"],
                )
                .properties(height=200)
                .configure_view(stroke="transparent", fill="transparent")
                .configure_axis(gridColor="#27272a", domainColor="#27272a")
            )
            st.altair_chart(grade_chart, use_container_width=True)

        # ── Compliance summary ────────────────────────────────────
        if "score" in df.columns:
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
