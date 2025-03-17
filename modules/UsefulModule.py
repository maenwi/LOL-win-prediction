import random

def list_train_test_split(data, test_size=0.2, random_seed=None):
    """
    리스트를 주어진 비율로 훈련 데이터와 테스트 데이터로 분할합니다.

    Parameters:
    - data: list, 분할할 리스트
    - test_size: float, 테스트 데이터의 비율 (0 < test_size < 1)
    - random_seed: int, 랜덤 시드 값 (재현성을 위해 사용)

    Returns:
    - train_data: list, 훈련 데이터
    - test_data: list, 테스트 데이터
    """

    if random_seed is not None:
        random.seed(random_seed)
    
    data_size = len(data)
    test_count = int(data_size * test_size)
    
    # 테스트 데이터의 인덱스 샘플링
    test_indices = random.sample(range(data_size), test_count)
    
    # 테스트 데이터와 훈련 데이터 분할
    test_data = [data[i] for i in test_indices]
    train_data = [data[i] for i in range(data_size) if i not in test_indices]
    
    return train_data, test_data