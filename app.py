import streamlit as st
from node import RaftNode
from cluster import RaftCluster


st.set_page_config(page_title="Raft Leader Election Simulator", layout="wide")
st.title("Raft Leader Election Simulator")

# 세션 상태 초기화
if "nodes" not in st.session_state:
    st.session_state.nodes = [RaftNode(1), RaftNode(2), RaftNode(3)]
    st.session_state.cluster = RaftCluster(st.session_state.nodes)

cluster = st.session_state.cluster
nodes = st.session_state.nodes


# 버튼 영역
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Next Tick"):
        cluster.tick()

with col2:
    if st.button("Crash Leader"):
        cluster.crash_leader()

with col3:
    if st.button("Reset"):
        st.session_state.nodes = [RaftNode(1), RaftNode(2), RaftNode(3)]
        st.session_state.cluster = RaftCluster(st.session_state.nodes)
        st.rerun()


# 노드 상태 표시
st.subheader("Cluster State")

state_colors = {
    "Follower": "#d9d9d9",
    "Candidate": "#ffe599",
    "Leader": "#b6d7a8",
    "Crashed": "#ea9999",
}

cols = st.columns(len(nodes))

for i, node in enumerate(nodes):
    with cols[i]:
        color = state_colors.get(node.state, "#ffffff")
        voted_for_display = node.voted_for if node.voted_for is not None else "-"

        if node.state == "Leader":
            timing_info = "<p><strong>Role:</strong> Sending heartbeats</p>"
        elif node.state == "Crashed":
            timing_info = "<p><strong>Status:</strong> No response</p>"
        else:
            timing_info = (
                f"<p><strong>Election Timeout:</strong> "
                f"{node.time_since_heartbeat}/{node.election_timeout}</p>"
            )

        st.markdown(
            f"""
            <div style="
                padding: 16px;
                border-radius: 12px;
                background-color: {color};
                color: black;
                text-align: center;
                border: 1px solid #999;
            ">
                <h3>Node {node.node_id}</h3>
                <p><strong>State:</strong> {node.state}</p>
                <p><strong>Term:</strong> {node.current_term}</p>
                <p><strong>Voted For:</strong> {voted_for_display}</p>
                {timing_info}
                <p><strong>Alive:</strong> {node.alive}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# 로그 영역
st.subheader("Event Log")

if cluster.logs:
    for log in reversed(cluster.logs):
        st.write(log)
else:
    st.write("No events yet.")
