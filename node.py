import random
from constants import FOLLOWER, CANDIDATE, LEADER, MIN_TIMEOUT, MAX_TIMEOUT


class RaftNode:
    def __init__(self, node_id: int):
        self.node_id = node_id

        # 기본 상태
        self.state = FOLLOWER
        self.alive = True

        # Raft 핵심 값
        self.current_term = 0
        self.voted_for = None
        self.votes_received = 0

        # timeout / heartbeat 관련
        self.election_timeout = 0
        self.time_since_heartbeat = 0
        self.reset_election_timeout()

    def reset_election_timeout(self):
        """
        새로운 election timeout을 랜덤하게 설정하고,
        heartbeat를 기다린 시간을 초기화
        """
        self.election_timeout = random.randint(MIN_TIMEOUT, MAX_TIMEOUT)
        self.time_since_heartbeat = 0

    def tick(self):
        """
        시간 1 증가
        leader가 아닌 노드는 heartbeat를 기다리는 시간이 증가함
        """
        if not self.alive:
            return

        if self.state != LEADER:
            self.time_since_heartbeat += 1

    def should_start_election(self) -> bool:
        """
        election 시작 여부 판단
        """
        return (
            self.alive
            and self.state != LEADER
            and self.time_since_heartbeat >= self.election_timeout
        )

    def become_follower(self, term: int):
        """
        follower 상태로 전환
        """
        self.state = FOLLOWER
        self.current_term = term
        self.voted_for = None
        self.votes_received = 0
        self.reset_election_timeout()

    def become_candidate(self):
        """
        candidate 상태로 전환
        - term 증가
        - 자기 자신에게 투표
        """
        self.state = CANDIDATE
        self.current_term += 1
        self.voted_for = self.node_id
        self.votes_received = 1
        self.reset_election_timeout()

        print(f"Node {self.node_id} became CANDIDATE (term {self.current_term})")

    def become_leader(self):
        """
        leader 상태로 전환
        """
        self.state = LEADER
        self.votes_received = 0

        print(f"Node {self.node_id} became LEADER (term {self.current_term})")

    def receive_heartbeat(self, leader_term: int):
        """
        leader로부터 heartbeat 수신
        """
        if not self.alive:
            return

        # leader term이 현재 term보다 같거나 높으면 follower 유지
        if leader_term >= self.current_term:
            self.state = FOLLOWER
            self.current_term = leader_term
            self.voted_for = None
            self.votes_received = 0
            self.reset_election_timeout()

    def request_vote(self, candidate_id: int, candidate_term: int) -> bool:
        """
        다른 candidate가 투표 요청을 보냈을 때 처리
        """
        if not self.alive:
            return False

        # 더 오래된 term이면 거절
        if candidate_term < self.current_term:
            return False

        # 더 새로운 term이면 follower로 전환
        if candidate_term > self.current_term:
            self.become_follower(candidate_term)

        # 아직 아무에게도 투표하지 않았거나, 이미 같은 candidate에게 투표한 경우 승인
        if self.voted_for is None or self.voted_for == candidate_id:
            self.voted_for = candidate_id
            self.reset_election_timeout()
            return True

        return False
