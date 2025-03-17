import requests
import pandas as pd
import numpy as np


class APIHander:
    """
    RIOT API에서 얻을 수 있는 api_key를 통해 데이터를 불러올 수 있는 클래스
    
    Attributes:
        api_key : RIOT API에서 발급 받은 api_key 입니다.
    
    """
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://kr.api.riotgames.com/lol/"

    def _make_response(self, endpoint, params, change_base_url = False, new_base_url = ""):
        self.response = requests.get(self.base_url + endpoint, params = params)
        if change_base_url:
            self.response = requests.get(new_base_url + endpoint, params = params)
            # print(response.url)
            # print(response.status_code)
        if self.response.status_code == 200:
            return self.response.json()
        else:
            raise Exception(f"API request failed with status {self.response.status_code}")
    
    def get_players_in_high_tier(self, queue, tier):
        # https://kr.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5?api_key=RGAPI-d5ec0d44-3eaa-4c76-904e-6a13855e5fbc
        endpoint = f"league/v4/{tier}leagues/by-queue/{queue}"
        params = {
            "api_key" : self.api_key
        }
        return self._make_response(endpoint, params)
    
    def get_players_in_tier(self, queue, division, tier, page):
        # https://kr.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/DIAMOND/I?page=100&api_key=RGAPI-0385985e-c9eb-4226-8712-8fc22d25b825
        endpoint = f"league/v4/entries/{queue}/{tier}/{division}"
        params = {
            "page" : page,
            "api_key" : self.api_key
        }
        return self._make_response(endpoint, params)
    
    def get_player_information(self, summoner_id):
        # https://kr.api.riotgames.com/lol/summoner/v4/summoners/7UTADmly1oxqAH65TaF8oKyq22oe24pNmekBeT4-9v2-_qDC?api_key=RGAPI-0385985e-c9eb-4226-8712-8fc22d25b825

        endpoint = f"summoner/v4/summoners/{summoner_id}"
        params = {
            "api_key" : self.api_key
        }
        
        return self._make_response(endpoint, params)
    
    def get_game_ids(self, puuid, queue, type, start = 0, count = 20):
        # https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/KO3vDELXr5SdXh0ivn47_NqK5T--BrLoe7ATOP_NZEYNz14C74fdt1h95uLoFKNzPXZrTlf1kG9-NA/ids
        # ?queue=420&type=ranked&start=0&count=20&api_key=RGAPI-d5ec0d44-3eaa-4c76-904e-6a13855e5fbc

        # https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/8d8ssHwVjjoqWIKEFhqwU6X1Th5DpAYL2clr7DF7Ftt5J6EbEGi04lI5r1gaDQkcGgjS4VJzjioF8w/ids
        # ?queue=420&type=ranked&start=0&count=30&api_key=RGAPI-0385985e-c9eb-4226-8712-8fc22d25b825
        base_url = "https://asia.api.riotgames.com/lol/"
        endpoint = f"match/v5/matches/by-puuid/{puuid}/ids"
        params = {
            "queue" : queue, #솔랭 : 420
            "type" : type, #ranked
            "start" : start, #0
            "count" : count, #몇 개의 게임을 셀건지?
            "api_key" : self.api_key
        }

        return self._make_response(endpoint, params, change_base_url=True, new_base_url=base_url)
    
    def get_game_timeline_information(self, game_id):
        # https://asia.api.riotgames.com/lol/match/v5/matches/KR_7328456203/timeline
        # ?api_key=RGAPI-d5ec0d44-3eaa-4c76-904e-6a13855e5fbc
        base_url = "https://asia.api.riotgames.com/lol/"
        endpoint = f"match/v5/matches/{game_id}/timeline"
        params = {
            "api_key" : self.api_key
        }

        return self._make_response(endpoint, params, change_base_url=True, new_base_url=base_url)
    
    def get_game_information(self, game_id):
        # https://asia.api.riotgames.com/lol/match/v5/matches/KR_7335746315
        # ?api_key=RGAPI-295c181a-ae9b-4499-97fd-b86ed23ef858
        base_url = "https://asia.api.riotgames.com/lol/"
        endpoint = f"match/v5/matches/{game_id}"
        params = {
            "api_key" : self.api_key
        }

        return self._make_response(endpoint, params, change_base_url=True, new_base_url=base_url)


class PositionFinder:
    """
    플레이어의 10분간 위치 정보를 기반으로 포지션을 찾아주는 클래스입니다.
    먼저 게임이 끝나는 시점에서 정글몬스터 처치 수(jungleMinionsKilled)가 제일 높은 플레이어를 정글러로 분류합니다.
    나머지 4명의 플레이어에 대해 1분부터 10분까지 매 분 기록된 위치 좌표의 평균값을 통해, 포지션을 찾아줍니다.
    """
    # def __init__(self):
    
    def find_jungler(self, a_game_timeline): #정글러를 찾아주는 함수
        self.game_end_min = len(a_game_timeline) - 1
        blue_jungle_cs = np.array(pd.DataFrame(a_game_timeline.loc[self.game_end_min,"participantFrames"]).loc["jungleMinionsKilled"][0:5])
        red_jungle_cs = np.array(pd.DataFrame(a_game_timeline.loc[self.game_end_min,"participantFrames"]).loc["jungleMinionsKilled"][5:10])

        blue_jungle_number = np.argmax(blue_jungle_cs) + 1
        red_jungle_number = np.argmax(red_jungle_cs) + 5 + 1

        return [blue_jungle_number, red_jungle_number]

    def get_cs(self, player_number, minute, a_game_timeline): #특정 라이너의 cs를 가져오는 함수
        # minute == N : N-1 분 ~ N 분 사이에 진행된 내용, N 분 정보
        if player_number in self.find_jungler(a_game_timeline):
            return a_game_timeline.loc[minute, "participantFrames"][str(player_number)]['jungleMinionsKilled']
        return a_game_timeline.loc[minute, "participantFrames"][str(player_number)]['minionsKilled']
    
    def find_positions(self, a_game_timeline): #포지션을 찾아주는 함수
        early_game = a_game_timeline.iloc[1:10,1]
        positions = early_game.apply(lambda one_minute_game : pd.Series(one_minute_game).apply(lambda x: [x['position']['x'], x['position']['y']]))
        # player_numbers = np.array(positions.columns)

        def compute_average_position(column):
            x_coordinate = column.apply(lambda x: x[0]).mean()
            y_coordinate = column.apply(lambda x: x[1]).mean()
            return x_coordinate - y_coordinate

        blue_average_position = np.array(positions.apply(compute_average_position))[0:5]
        red_average_position = np.array(positions.apply(compute_average_position))[5:10]

        jungler_numbers = self.find_jungler(a_game_timeline) # 여기서는 정글러의 플레이어 번호를 줌
        jungler_indices = [jungler_numbers[0] - 1, jungler_numbers[1] - 5 - 1]
        # 이를 각 팀에서의 index로 변환

        blue_mask = np.arange(len(blue_average_position)) != jungler_indices[0]
        red_mask = np.arange(len(red_average_position)) != jungler_indices[1]

        blue_average_position = pd.Series(blue_average_position[blue_mask])
        red_average_position = pd.Series(red_average_position[red_mask])

        blue_average_position = blue_average_position.rank(ascending=True)
        red_average_position = red_average_position.rank(ascending=True)

        position_name = {1: 'TOP', 2: 'MID', 3: 'BOT', 4: 'BOT'}
        blue_position_result = list(blue_average_position.map(lambda x: position_name[int(x)]))
        # 블루팀 탑, 미드, 바텀 두명을 위치 기반으로 분류한 결과
        blue_position_result = blue_position_result[0:jungler_indices[0]] + ["JUG"] + blue_position_result[jungler_indices[0]:4]
        red_position_result = list(red_average_position.map(lambda x: position_name[int(x)]))
        # 레드팀 탑, 미드, 바텀 두명을 위치 기반으로 분류한 결과
        red_position_result = red_position_result[0:jungler_indices[1]] + ["JUG"] + red_position_result[jungler_indices[1]:4]

        blue_BOTs = [i for i, value in enumerate(blue_position_result) if value == 'BOT']
        red_BOTs = [i for i, value in enumerate(red_position_result) if value == 'BOT']

        # 원딜과 서폿의 cs 비교로 원딜 서폿 확인
        # 이때, a_game_timeline 에 들어있는 index와 blue_BOTs 의 index에 차이가 있으므로 그거 조정해줘야함
        # red도 마찬가지
        if self.get_cs(blue_BOTs[0] + 1, self.game_end_min, a_game_timeline) > self.get_cs(blue_BOTs[1] + 1, self.game_end_min, a_game_timeline):
            blue_position_result[blue_BOTs[0]] = "ADC"
            blue_position_result[blue_BOTs[1]] = "SUP"
        else:
            blue_position_result[blue_BOTs[1]] = "ADC"
            blue_position_result[blue_BOTs[0]] = "SUP"

        if self.get_cs(red_BOTs[0] + 5 + 1, self.game_end_min, a_game_timeline) > self.get_cs(red_BOTs[1] + 5 + 1, self.game_end_min, a_game_timeline):
            red_position_result[red_BOTs[0]] = "ADC"
            red_position_result[red_BOTs[1]] = "SUP"
        else:
            red_position_result[red_BOTs[1]] = "ADC"
            red_position_result[red_BOTs[0]] = "SUP"

        return [blue_position_result, red_position_result]
    
    # def summary_information_at_min(self, minute): #특정 분의 게임 정보를 저장하는 함수
    #     # 하나의 긴 데이터프레임으로 나오도록


class EventRecorder(PositionFinder):
    """
    timeline 데이터에서, 원하는 event를 기록할 수 있는 함수
    
    interseting_events 에 원하는 event를 지정해서,
    뭘 기록하고 뭘 기록하지 않을지 지정할 수 있음.
    """
    def __init__(self):
        # super().__init__()
        self.interseting_events = ["CHAMPION_KILL", "ELITE_MONSTER_KILL", 
                                   "TURRET_PLATE_DESTROYED", "BUILDING_KILL", "GAME_END", "LEVEL_UP"]

        # 현재 게임 내에서, 각 플레이어가 어느 포지션인지 확인
        # a_game_timeline은 외부에서 넣어줘야함.
        # 이거는 근데 클래스 선언 시에는 할 필요는 없어 보이고, 언제 해야 효율적이지?
        # 클래스를 선언 할
        # self.game_positions = super().find_positions(self.a_game_timeline)
        
        # score_board
        self.record_KDACS = {f"{pos}_{KDACS}" : 0 for pos in range(1,11) for KDACS in ["K", "D", "A", "CS"]}
        self.record_object = {f"{team}_{obj_name}" : 0 for team in ["blue", "red"] for obj_name in ["HORDE", "DRAGON", "ELDER_DRAGON", "RIFTHERALD","BARON_NASHOR"]}
        self.record_turret_plate = {f"{team}_{lane}_TURRET_PLATE" : 0 for team in ["blue", "red"] for lane in ["TOP","MID","BOT"]}
        self.record_building = {f"{team}_{lane}_{type_of_building}" : 0 for team in ["blue", "red"] for lane in ["TOP","MID","BOT"] for type_of_building in ["TURRET", "INHIBITOR"]}
        self.record_building["blue_NEXUS_TURRET"] = 0
        self.record_building["red_NEXUS_TURRET"] = 0
        self.record_blue_win = {"blue_win" : 0}
        self.record_level = {f"{pos}_LEVEL" : 1 for pos in range(1,11)}
        # INHIBITOR_BUILDING, TOWER_BUILDING
        # INNER_TURRET, OUTER_TURRET, BASE_TURRET(억제기 포탑), NEXUS_TURRET
        # score_board_columns_objects = [f"{object_name}" for object_name in []]

    
    # private_or_not : 팀의 이득인지, 개인의 이득인지
    # score_id : 점수를 낸 사람의 number
    # victim_id : 죽은 사람의 number
    # assist_ids : 어시스트 한 사람들의 number의 list

    def update_score_board_from_CS(self, player_number, minute, a_game_timeline):
        self.record_KDACS[f"{player_number}_CS"] = self.get_cs(player_number, minute, a_game_timeline)
        return

    def update_score_board_from_CHAMPION_KILL(self, each_event):
        killer_id = int(each_event['killerId'])
        victim_id = int(each_event['victimId'])
        # 솔로킬은 어시스트가 기록 안되는듯 : assistingParticipantIds가 아에 생성이 되질 않음.
        try:
            if isinstance(each_event['assistingParticipantIds'], list):
                assist_ids = list(map(int, each_event['assistingParticipantIds']))
                for assist_id in assist_ids:
                    self.record_KDACS[f"{assist_id}_A"] += 1
        except:
            assist_ids = []

        if killer_id != 0: # 처형인 경우, killer id가 기록이 안 되어있음. 이 경우 데스만 추가
            self.record_KDACS[f"{killer_id}_K"] += 1
        self.record_KDACS[f"{victim_id}_D"] += 1

        return 
    
    def update_score_board_from_ELITE_MONSTER_KILL(self, each_event):
        score_team = "blue" if each_event['killerTeamId'] == 100 else "red"
        obj_name = each_event["monsterType"]

        self.record_object[f"{score_team}_{obj_name}"] += 1

        return 

    def update_score_board_from_TURRET_PLATE_DESTROYED(self, each_event):
        # 포탑 방패는 파괴된 입장에서 기록되어 있음.
        # 따라서 점수를 딴 팀은 반대로 기록해야함.
        # 여기서는, 상대 팀의 어느 라인의 포탑 방패를 몇개 깠냐로 볼 거임.
        # ex) blue_TOP_
        score_team = "blue" if each_event["teamId"] == 200 else "red"
        lane_type = each_event["laneType"].split("_")[0]

        self.record_turret_plate[f"{score_team}_{lane_type}_TURRET_PLATE"] += 1

        return 

    def update_score_board_from_BUILDING_KILL(self, each_event):
        score_team = "blue" if each_event["teamId"] == 200 else "red"
        lane_type = each_event["laneType"].split("_")[0]
        building_type = "TURRET" if each_event["buildingType"] == "TOWER_BUILDING" else "INHIBITOR"
        if building_type == "TURRET":
            tower_type = each_event["towerType"]
            if tower_type == "NEXUS_TURRET":
                self.record_building[f"{score_team}_{tower_type}"] += 1
            else:
                # 라인 별로 타워 부신 수 추가
                self.record_building[f"{score_team}_{lane_type}_{building_type}"] += 1
        else:
            # 억제기 파괴 수 추가
            self.record_building[f"{score_team}_{lane_type}_{building_type}"] += 1

        return 

    def update_score_board_from_LEVEL_UP(self, each_event):
        self.record_level[f"{int(each_event["participantId"])}_LEVEL"] += 1
        return 
    
    def update_score_board_from_GAME_END(self, each_event):
        self.record_blue_win["blue_win"] = 1 if each_event["winningTeam"] == 100 else 0
        return 
    
    # def update_score_board_ITEM_PURCHASED(self, each_event):
    #     return
    
    # def update_score_board_ITEM_DESTROYED(self, each_event):
    #     return
    
    # def update_score_board_ITEM_SOLD(self, each_event):
    #     return

    def update_score_board(self, each_event):
        # 만약 우리가 찾는 row 가 아니면
        if each_event['type'] not in self.interseting_events:
            return  # 함수는 종료
        # 우리가 찾고 있는 row라면
        else:
            event_name = each_event['type']
            # print(event_name)
            # 게임 정보 기록
            function_name = f"update_score_board_from_{event_name}"
            getattr(self, function_name)(each_event)


