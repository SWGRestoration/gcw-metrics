import json
import pandas as pd
import streamlit as st

def show_latest_event(path):
    st.title('Latest Shatterpoint')
    if not path.exists():
        st.info('The latest event data has not been exported yet.')
        return
    event=json.loads(path.read_text())
    title=event['event_type'].removeprefix('shatterpoint_').replace('_',' ').title()
    st.subheader(f"{title} · {event['planet'].title()}")
    st.caption(f"{event['start']} to {event['end'] or 'In progress'} · UTC")
    st.caption(event['coverage'])
    st.write('Crisis movement is shown separately from regional control points. Positive movement favors Imperial; negative movement favors Rebel.')
    df=pd.DataFrame(event['results'])
    if df.empty:
        st.info('No Crisis results have been observed for this event.')
        return
    a,b=st.columns(2)
    a.metric('Recorded results', f'{len(df):,}')
    b.metric('Net recorded Imperial movement',f'{df.signedImperialMovement.sum():+,}')
    st.subheader('Recorded movement by event source')
    summary=df.groupby('source').agg(results=('appliedMovement','size'),requested_movement=('requestedMovement','sum'),applied_movement=('appliedMovement','sum'),net_imperial_movement=('signedImperialMovement','sum'))
    st.dataframe(summary,use_container_width=True)
    st.caption('Requested and applied movement are logged magnitudes. Net movement is signed. These sums do not establish the overall winner or include unlogged/admin changes.')
    st.subheader('Crisis result details')
    st.dataframe(df[['logTimestamp','source','requestedMovement','appliedMovement','previousImperial','newImperial','signedImperialMovement']],use_container_width=True,hide_index=True)
