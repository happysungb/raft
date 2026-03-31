from constants import LEADER, HEARTBEAT_INTERVAL


class RaftCluster:
    def __init__(self, nodes):
        self.nodes = nodes
        self.logs = []
        self.heartbeat_timer = 0

    def add_log(self, message: str):
        self.logs.append(message)
        if len(self.logs) > 15:
            self.logs.pop(0)

    def get_leader(self):
        leaders = [node for node in self.nodes if node.state == LEADER and node.alive]
        return leaders[0] if leaders else None

    def tick(self):
        # 1. 모든 노드 시간 1 증가
        for node in self.nodes:
            node.tick()

        # 2. 현재 leader 확인
        leader = self.get_leader()

        # 3. leader가 있으면 heartbeat 전송
        if leader:
            self.heartbeat_timer += 1

            if self.heartbeat_timer >= HEARTBEAT_INTERVAL:
                self.heartbeat_timer = 0

                for node in self.nodes:
                    if node.node_id != leader.node_id:
                        node.receive_heartbeat(leader.current_term)

                # self.add_log(
                #    f"Leader Node {leader.node_id} sent heartbeat (term {leader.current_term})"
                # )
            return

        # 4. leader가 없으면 election 시작할 노드 찾기
        for node in self.nodes:
            if node.should_start_election():
                self.start_election(node)
                break

    def start_election(self, candidate):
        candidate.become_candidate()
        self.add_log(
            f"Node {candidate.node_id} started election (term {candidate.current_term})"
        )

        # 다른 노드들에게 vote 요청
        for node in self.nodes:
            if node.node_id == candidate.node_id:
                continue

            granted = node.request_vote(candidate.node_id, candidate.current_term)

            if granted:
                candidate.votes_received += 1
                self.add_log(f"Node {node.node_id} voted for Node {candidate.node_id}")

        # 과반수 계산
        alive_nodes = sum(1 for node in self.nodes if node.alive)
        majority = alive_nodes // 2 + 1

        if candidate.votes_received >= majority:
            candidate.become_leader()
            self.add_log(
                f"Node {candidate.node_id} became Leader (term {candidate.current_term})"
            )
        else:
            self.add_log(
                f"Node {candidate.node_id} failed to win election "
                f"({candidate.votes_received}/{majority} votes)"
            )

    def crash_leader(self):
        leader = self.get_leader()
        if leader:
            leader.alive = False
            leader.state = "Crashed"
            self.add_log(f"Leader Node {leader.node_id} crashed")

    def reset_cluster(self, nodes):
        self.nodes = nodes
        self.logs = []
        self.heartbeat_timer = 0
