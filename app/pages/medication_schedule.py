"""Medication schedule generator page."""

import streamlit as st
from core.schedule.schedule_generator import ScheduleGenerator
from core.schedule.schedule_formatter import ScheduleFormatter
from core.schedule.reminder_exporter import ReminderExporter


def show():
    """Show medication schedule page."""
    st.header("📅 Medication Schedule")
    st.markdown("Generate daily medication schedules and reminders.")
    
    if not st.session_state.current_prescription:
        st.warning("Please parse a prescription first.")
        return
    
    # Generate schedule
    generator = ScheduleGenerator()
    schedule = generator.generate(st.session_state.current_prescription)
    
    # Display
    st.subheader("Daily Schedule")
    
    for slot in ['morning', 'afternoon', 'evening', 'night', 'as_needed']:
        items = schedule.get(slot, [])
        if not items:
            continue
        
        with st.expander(f"{slot.capitalize()} ({len(items)} medications)"):
            for item in items:
                st.write(f"**{item.time_display}**: {item.medication} {item.strength or ''}")
                if item.with_food:
                    st.caption("🍽️ Take with food")
                if item.special_instructions:
                    st.caption(f"Note: {item.special_instructions}")
    
    # Export options
    st.subheader("Export")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Export as Text"):
            formatter = ScheduleFormatter()
            text = formatter.to_text(schedule)
            st.download_button(
                "Download Schedule",
                text,
                file_name="medication_schedule.txt"
            )
    
    with col2:
        if st.button("Export Calendar (iCal)"):
            exporter = ReminderExporter()
            ical_path = exporter.to_ical(schedule)
            with open(ical_path, 'rb') as f:
                st.download_button(
                    "Download iCal",
                    f,
                    file_name="medication_schedule.ics"
                )