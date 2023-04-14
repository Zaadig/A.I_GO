import requests
import zipfile
import tarfile
import tempfile
import os
import re
import numpy as np
import pickle
from sgfmill import sgf, boards
import random
from sklearn.model_selection import train_test_split


def sanitize_filename(filename):
    return re.sub(r'[<>:"\\/|?*]', '_', filename)


def download_and_extract_datasets(dataset_urls):
    temp_dir = tempfile.mkdtemp()

    for url in dataset_urls:
        response = requests.get(url, stream=True)
        file_name = url.split("/")[-1]

        with open(os.path.join(temp_dir, file_name), "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        if file_name.endswith(".zip"):
            with zipfile.ZipFile(os.path.join(temp_dir, file_name), "r") as zip_ref:
                for member in zip_ref.infolist():
                    member.filename = sanitize_filename(member.filename)
                    zip_ref.extract(member, temp_dir)
        elif file_name.endswith(".tgz") or file_name.endswith(".tar.gz"):
            with tarfile.open(os.path.join(temp_dir, file_name), "r:gz") as tar_ref:
                for member in tar_ref.getmembers():
                    member.name = sanitize_filename(member.name)
                    tar_ref.extract(member, temp_dir)

    return temp_dir


def parse_sgf_file(file_path):
    with open(file_path, "rb") as f:
        sgf_content = f.read()
    game = sgf.Sgf_game.from_bytes(sgf_content)

    # Extract information
    root = game.get_root()

    player_black = root.get("PB")
    if player_black is None:
        player_black = "Unknown"

    player_white = root.get("PW")
    if player_white is None:
        player_white = "Unknown"

    player_rank = (player_black, player_white)
    handicap = game.get_handicap()
    komi = game.get_komi()

    # Extract the result from the game properties
    if (game.get_root().has_property('RE')):
        result = game.get_root().get_raw('RE')
    else:
        result = "Unknown"

    moves = []
    for node in game.main_sequence_iter():
        move = node.get_move()
        moves.append(move)

    return player_rank, handicap, komi, result, moves



def preprocess_moves(moves):
    board_size = 9
    preprocessed_moves = []

    for move in moves:
        if move is None:  # Pass move
            one_hot_move = np.zeros((board_size, board_size, 3))
            one_hot_move[:, :, 2] = 1
        else:
            color, coords = move
            if coords is None:
                continue
            x, y = coords
            if x >= board_size or y >= board_size:
                continue 

            one_hot_move = np.zeros((board_size, board_size, 3))

            if color == 'b':
                one_hot_move[x, y, 0] = 1
            else:
                one_hot_move[x, y, 1] = 1

        preprocessed_moves.append(one_hot_move)
    return preprocessed_moves


def collect_sgf_files(sgf_dir):
    sgf_files = []
    for root, _, files in os.walk(sgf_dir):
        sgf_files.extend([os.path.join(root, f) for f in files if f.endswith(".sgf")])
    return sgf_files

def pad_moves(preprocessed_moves):
    if not preprocessed_moves:
        return []

    max_length = max(len(moves) for moves in preprocessed_moves)
    padded_moves = []
    for moves in preprocessed_moves:
        padded_moves.append(np.pad(moves, ((0, max_length - len(moves)), (0, 0), (0, 0)), mode='constant'))
    return padded_moves


def create_datasets(data_dir, train_ratio=0.8, val_ratio=0.1, random_seed=42):
    all_files = collect_sgf_files(data_dir)

    # Split the files into train, validation, and test sets
    train_files, temp_files = train_test_split(all_files, train_size=train_ratio, random_state=random_seed)
    test_ratio = 1 - (train_ratio + val_ratio)
    val_files, test_files = train_test_split(temp_files, test_size=test_ratio/(val_ratio + test_ratio), random_state=random_seed)

    train_set, val_set, test_set = [], [], []

    # Process training files
    for file in train_files:
        player_rank, handicap, komi, result, moves = parse_sgf_file(file)
        if not moves:
            print(f"No moves found in file: {file}")
            continue
        preprocessed_moves = preprocess_moves(moves)
        padded_moves = pad_moves(preprocessed_moves)
        train_set.append((player_rank, handicap, komi, result, padded_moves))

    # Process validation files
    for file in val_files:
        player_rank, handicap, komi, result, moves = parse_sgf_file(file)
        if not moves:
            print(f"No moves found in file: {file}")
            continue
        preprocessed_moves = preprocess_moves(moves)
        padded_moves = pad_moves(preprocessed_moves)
        val_set.append((player_rank, handicap, komi, result, padded_moves))

    # Process test files
    for file in test_files:
        player_rank, handicap, komi, result, moves = parse_sgf_file(file)
        if not moves:
            print(f"No moves found in file: {file}")
            continue
        preprocessed_moves = preprocess_moves(moves)
        padded_moves = pad_moves(preprocessed_moves)
        test_set.append((player_rank, handicap, komi, result, padded_moves))

    return train_set, val_set, test_set





dataset_urls = [
    "https://dl.dropboxusercontent.com/s/ctr1h954vauiej5/go9_20160729_119x200.tgz",
    "https://dl.dropboxusercontent.com/s/7hzopmr000ndham/go9_20170307_200x200.zip",
    "https://dl.dropboxusercontent.com/s/abpzmqrw7gyvlzt/go9.tgz"
]


data_dir = download_and_extract_datasets(dataset_urls)

train_set, val_set, test_set = create_datasets(data_dir)

print("Length of train_set:", len(train_set))
print("Length of val_set:", len(val_set))
print("Length of test_set:", len(test_set))


def print_sample(sample):
    player_rank, handicap, komi, result, preprocessed_moves = sample
    print("Player Rank:", player_rank)
    print("Handicap:", handicap)
    print("Komi:", komi)
    print("Result:", result)
    print("Number of preprocessed moves:", len(preprocessed_moves))

print("Sample from train_set:")
print_sample(random.choice(train_set))
print("\nSample from val_set:")
print_sample(random.choice(val_set))
print("\nSample from test_set:")
print_sample(random.choice(test_set))


with open("train_set.pickle", "wb") as f:
    pickle.dump(train_set, f)

with open("val_set.pickle", "wb") as f:
    pickle.dump(val_set, f)

with open("test_set.pickle", "wb") as f:
    pickle.dump(test_set, f)
