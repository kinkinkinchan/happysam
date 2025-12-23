import pyxel

font = pyxel.Font("k8x12.bdf")

pyxel.init(255, 200, title="HappyBirthDay!", fps=30)

# 🎵 BGM（Happy Birthday to You）
pyxel.sounds[1].set(
    "C4 C4 D4 C4 C4 F4 E4 E4 R "
    "C4 C4 D4 C4 C4 G4 F4 F4 R "
    "C4 C4 A4 A4 F4 E4 D4 D4 D4 R R "
    "A4 A4 F4 F4 G4 G4 F4 F4 F4 R R R ",
    "T", "5", "N", 60
)
pyxel.musics[0].set([1])

# 🔑 効果音：鍵が開く音
pyxel.sounds[2].set("C3 G3 C4 R", "T", "3", "N", 8)

# 🎵 room1用BGM
pyxel.sounds[0].set(
    "C4 E4 G4 B4 G4 E4 C4 D4 F4 A4 F4 D4 C4 "
    "E4 G4 C4 A4 F4 D4 B3 C4 E4 G4 E4 D4 C4",
    "T", "1", "F", 50
)
pyxel.play(0, 0, loop=True)

# 画像読み込み
pyxel.images[0].load(0, 0, "assets/room.png", True)
pyxel.images[2].load(0, 0, "assets/window.png")
pyxel.images[1].load(0, 0, "assets/chara_top.png")
pyxel.images[1].load(32, 0, "assets/chara_left.png")
pyxel.images[1].load(64, 0, "assets/chara_right.png")
pyxel.images[1].load(96, 0, "assets/chara_back.png")
pyxel.images[2].load(0, 64, "assets/cat.png")  # 🐱 猫画像を右側に

# 🎮 初期座標（PC前に調整）
player_x, player_y = 120, 135
player_dir = "front"
player_size = 32

show_message = None
show_letter = False
visited_objects = set()
room_opened = False
current_room = "room1"
tv_turned_on = False  # 📺 テレビが点いたかどうかの状態管理
bed_door_enabled = False  # 寝室の扉が調べられるようになったか
bedroom_entered = False  # 寝室に移動したかどうか
exit_to_room1 = False  # 🏠 リビングに戻る準備中かどうか
genkan_unlocked = False  # 🚪 玄関へ行けるようになったかどうか
show_genkan_message = False
cat_visible = False  # 🐱 猫を表示するかどうか
cat_interacted = False
room2_unlocked = False

# room1の調査対象オブジェクト
all_objects = {
    "nemo_bag", "reizouko", "right_shelf", "lamp", "aircleaner",
    "tv_shelf", "tsumetogi", "table", "gomibako", "pc"
}

# 寝室の調査対象オブジェクト（ドアを除く）
bedroom_objects = {
    "bat", "painting", "box", "fire", "shelf1_1", "shelf1_2", "shelf1_3", "shelf1_4", "shelf1_5",
    "shelf2_1", "shelf2_2", "shelf2_3", "shelf2_4", "shelf2_5", "shelf2_6",
    "shelf3_1", "shelf3_2", "shelf3_3", "shelf3_4", "shelf3_5",
}
visited_bedroom_objects = set()

def update():
    global player_x, player_y, player_dir, show_message
    global room_opened, current_room, show_letter
    global tv_turned_on, bed_door_enabled, bedroom_entered, exit_to_room1, genkan_unlocked, show_genkan_message
    global cat_visible
    global cat_interacted, room2_unlocked
    old_x, old_y = player_x, player_y

    # キャラ移動
    if pyxel.btn(pyxel.KEY_UP):
        player_y -= 2
        player_dir = "back"
    elif pyxel.btn(pyxel.KEY_DOWN):
        player_y += 2
        player_dir = "front"
    elif pyxel.btn(pyxel.KEY_LEFT):
        player_x -= 2
        player_dir = "left"
    elif pyxel.btn(pyxel.KEY_RIGHT):
        player_x += 2
        player_dir = "right"

    # 画面外に出ないよう制御
    player_x = max(0, min(player_x, 255 - player_size))
    player_y = max(0, min(player_y, 200 - player_size))

    # 当たり判定
    if is_colliding(player_x, player_y):
        player_x, player_y = old_x, old_y

    # Enterキー押下時の挙動
    if pyxel.btnp(pyxel.KEY_RETURN):
        if show_letter:
            show_letter = False
            return
        if show_message == "room_open":
            show_message = None
            room_opened = True
            bed_door_enabled = True
            return
        elif show_message:
            if show_message == "left_corner":
                show_message = None
                show_letter = True
                return

            # 📺 テレビを消す
            if show_message == "tv_shelf" and tv_turned_on:
                pyxel.images[0].load(0, 0, "assets/room.png", True)
                pyxel.images[2].load(0, 0, "assets/window.png")
                pyxel.images[1].load(0, 0, "assets/chara_top.png")
                pyxel.images[1].load(32, 0, "assets/chara_left.png")
                pyxel.images[1].load(64, 0, "assets/chara_right.png")
                pyxel.images[1].load(96, 0, "assets/chara_back.png")
                tv_turned_on = False

            # 寝室へ移動
            if show_message == "bed_door":
                pyxel.images[0].load(0, 0, "assets/bedroom.png", True)
                player_x, player_y = 195, 35  # 🚪 寝室のドア前に初期位置を移動
                pyxel.images[2].load(0, 0, "assets/window.png")
                pyxel.images[1].load(0, 0, "assets/chara_top.png")
                pyxel.images[1].load(32, 0, "assets/chara_left.png")
                pyxel.images[1].load(64, 0, "assets/chara_right.png")
                pyxel.images[1].load(96, 0, "assets/chara_back.png")
                current_room = "bedroom"  # 🛏️ 寝室状態に切り替え
                bedroom_entered = True
            if show_message == "exit_to_room1":
                # 🏠 room1 に戻る処理
                pyxel.images[0].load(0, 0, "assets/room.png", True)
                player_x, player_y = 50, 60  # 左上ドア前
                pyxel.images[2].load(0, 0, "assets/window.png")
                pyxel.images[1].load(0, 0, "assets/chara_top.png")
                pyxel.images[1].load(32, 0, "assets/chara_left.png")
                pyxel.images[1].load(64, 0, "assets/chara_right.png")
                pyxel.images[1].load(96, 0, "assets/chara_back.png")
                current_room = "room1"
                show_message = None
                exit_to_room1 = False
                return
            if show_message == "go_genkan":
                player_x, player_y = 115, 60  # 左上ドア前
                pyxel.images[0].load(0, 0, "assets/genkan.png")
                pyxel.images[2].load(0, 0, "assets/window.png")
                pyxel.images[1].load(0, 0, "assets/chara_top.png")
                pyxel.images[1].load(32, 0, "assets/chara_left.png")
                pyxel.images[1].load(64, 0, "assets/chara_right.png")
                pyxel.images[1].load(96, 0, "assets/chara_back.png")
                current_room = "genkan"       # ← これを追加！
                show_message = None
                return
            if show_message == "genkan_door_exit":
                pyxel.images[0].load(0, 0, "assets/room.png", True)
                player_x, player_y = 0, 140
                current_room = "room1"
                cat_visible = True
                show_message = None
                return
            if show_message == "genkan_open":
                show_message = None
                return
            
            if show_message == "go_room2":
                pyxel.stop(0)  # 🎵 room1 BGM を停止
                pyxel.play(0, 1, loop=True)  # 🎵 Happy Birthday BGM を再生
                pyxel.images[0].load(0, 0, "assets/room2.png", True)
                player_x, player_y = 90, 35  # 🎮 上ドア前に初期位置
                pyxel.images[2].load(0, 0, "assets/window.png")
                pyxel.images[1].load(0, 0, "assets/chara_top.png")
                pyxel.images[1].load(32, 0, "assets/chara_left.png")
                pyxel.images[1].load(64, 0, "assets/chara_right.png")
                pyxel.images[1].load(96, 0, "assets/chara_back.png")
                pyxel.images[2].load(0, 100, "assets/letter.png")  # 100はcat.pngやwindow.pngとかぶらない範囲
                current_room = "room2"
                show_message = None
                return
            if not room_opened and all_objects <= visited_objects:
                show_message = "room_open"
                pyxel.play(1, 2)
                return
            
            if show_message == "room2_exit_door":
                pyxel.stop(0)  # 🎵 Happy Birthday を止める
                pyxel.play(0, 0, loop=True)  # 🎵 room1 BGM を再生
                pyxel.images[0].load(0, 0, "assets/room.png", True)
                player_x, player_y = 50, 180  # 左上ドア前などに戻す
                pyxel.images[2].load(0, 0, "assets/window.png")
                pyxel.images[1].load(0, 0, "assets/chara_top.png")
                pyxel.images[1].load(32, 0, "assets/chara_left.png")
                pyxel.images[1].load(64, 0, "assets/chara_right.png")
                pyxel.images[1].load(96, 0, "assets/chara_back.png")
                current_room = "room1"
                show_message = None
                return
            
            if show_message == "room2_kin":
                show_message = None
                show_letter = True  # 📩 手紙を表示するようにする
                return

            show_message = None
            

        else:
            if current_room == "room1":
                for obj in all_objects:
                    if check_near(player_x, player_y, obj):
                        visited_objects.add(obj)
                        show_message = obj
                        if obj == "tv_shelf" and not tv_turned_on:
                            pyxel.images[0].load(0, 0, "assets/tvon.png")
                            pyxel.images[2].load(0, 0, "assets/window.png")
                            pyxel.images[1].load(0, 0, "assets/chara_top.png")
                            pyxel.images[1].load(32, 0, "assets/chara_left.png")
                            pyxel.images[1].load(64, 0, "assets/chara_right.png")
                            pyxel.images[1].load(96, 0, "assets/chara_back.png")
                            tv_turned_on = True
                        return
                if bed_door_enabled and check_near(player_x, player_y, "bed_door"):
                    show_message = "bed_door"
                    return
                if genkan_unlocked and check_near(player_x, player_y, "genkan_door"):
                    show_message = "go_genkan"
                    return
                # 🐱 猫を調べる（画面左下あたりに設置）
                if check_near(player_x, player_y, "cat"):
                    show_message = "cat"
                    if not cat_interacted:
                        cat_interacted = True
                        if not room2_unlocked:
                            show_message = "room2_unlock"
                            room2_unlocked = True
                            pyxel.play(1, 2)  # 🔑 ガチャッという効果音を再生
                    return
                if room2_unlocked and check_near(player_x, player_y, "room2_door"):
                    show_message = "go_room2"
                    return
            elif current_room == "bedroom":
                checked_any = False
                for obj in bedroom_objects:
                    if check_near(player_x, player_y, obj):
                        visited_bedroom_objects.add(obj)
                        show_message = obj
                        checked_any = True
                        if visited_bedroom_objects >= bedroom_objects and not genkan_unlocked:
                            show_genkan_message = True

                # 🏠 いつでも exit_door を調べられる
                if check_near(player_x, player_y, "exit_door"):
                    if not genkan_unlocked and show_genkan_message:
                        show_message = "genkan_open"
                        genkan_unlocked = True
                        pyxel.play(1, 2)  # 🔑 ガチャッという効果音を再生
                    else:
                        show_message = "exit_to_room1"
                        exit_to_room1 = True
                    checked_any = True

                if checked_any:
                    return
            elif current_room == "genkan":
                # 🎁 プレゼントを調べる
                if check_near(player_x, player_y, "present"):
                    show_message = "present"
                    return
                if check_near(player_x, player_y, "genkan_door_exit"):
                    if show_message != "genkan_door_exit":
                        show_message = "genkan_door_exit"
                    else:
            # Enterで戻る処理
                        pyxel.images[0].load(0, 0, "assets/room.png", True)
                        pyxel.images[2].load(0, 0, "assets/window.png")
                        pyxel.images[1].load(0, 0, "assets/chara_top.png")
                        pyxel.images[1].load(32, 0, "assets/chara_left.png")
                        pyxel.images[1].load(64, 0, "assets/chara_right.png")
                        pyxel.images[1].load(96, 0, "assets/chara_back.png")
                        current_room = "room1"
                        player_x, player_y = 0, 140
                        cat_visible = True
                        show_message = None
                    return
            elif current_room == "room2":  # ← ここに追加！
                if check_near(player_x, player_y, "room2_exit_door"):
                    show_message = "room2_exit_door"
                    return
                if check_near(player_x, player_y, "room2_obj1"):
                    show_message = "room2_obj1"
                    return
                if check_near(player_x, player_y, "room2_obj2"):
                    show_message = "room2_obj2"
                    return
                if check_near(player_x, player_y, "room2_food_table"):
                    show_message = "room2_food_table"
                    return
                if check_near(player_x, player_y, "room2_dishes"):
                    show_message = "room2_dishes"
                    return
                if check_near(player_x, player_y, "room2_flower"):
                    show_message = "room2_flower"
                    return
                if check_near(player_x, player_y, "room2_kin"):
                    show_message = "room2_kin"
                    return
                if check_near(player_x, player_y, "room2_pink"):
                    show_message = "room2_pink"
                    return


def is_colliding(x, y):
    px, py = x + player_size // 2, y + player_size // 2
    if current_room == "room1":
        collision_areas = [
            (0, 0, 255, 50),       # 上壁
            (85, 0, 115, 65),      # 荷物
            (0, 0, 45, 75),        # 冷蔵庫
            (215, 0, 255, 65),     # 右壁（花瓶や棚）
            (230, 115, 255, 200),  # ライト
            (200, 145, 230, 200),  # 空気清浄機
            (110, 0, 210, 85),     # TV棚
            (35, 120, 85, 170),    # つめとぎ
            (110, 95, 210, 150),   # テーブル
            (100, 160, 210, 200),  # ごみばこ
            (110, 155, 200, 200),  # ソファ背面
        ]
        if cat_visible and current_room == "room1":
            collision_areas.append((40, 100, 72, 132))  # 🐱 猫の当たり判定（中央上あたり）
    elif current_room == "bedroom":  # 🛏️ 寝室用の当たり判定
        collision_areas = [
            (0, 0, 255, 50),        # 上壁
            (0, 0, 5, 255),         # 左壁
            (250, 0, 255, 200),     # 右壁
            (0, 195, 255, 200),     # 下壁
            (0, 0, 170, 60),        # テーブル1
            (0, 67, 170, 115),      # テーブル2
            (0, 125, 170, 165),     # テーブル3
            (170, 135, 190, 165),   # 焚火
            (212, 115, 255, 200),   # 段ボール
        ]
    elif current_room == "room2":
        collision_areas = [
            (0, 0, 255, 50),       # 上の壁
            (0, 0, 10, 200),       # 左の壁
            (245, 0, 255, 200),    # 右の壁
            (0, 190, 255, 200),    # 下の壁
            (85, 60, 195, 140),    # ケーキテーブル
            (120, 30, 188, 140),    # ケーキ凸
            (0, 153, 255, 200),    # 下の食事台
            (180, 148, 255, 200),    # 下の食事かかたづけ
            (220, 125, 255, 200),    # 花
            (225, 0, 255, 110),    # kin
            (190, 0, 255, 90),   # プレゼント山
            (0, 0, 70, 80),     # ピンクのキャラ
        ]


    elif current_room == "genkan":
        collision_areas = [
            (0, 0, 255, 75),     # 上の壁（茶色＋ドアまわり）
            (0, 140, 255, 200),  # 下の床（グレー）
            (150, 95, 255, 200),  # くつばこ
            (0, 0, 65, 200),      # 左の壁
            (190, 0, 255, 200),  # 右の壁
            (110, 90, 145, 120),  # プレゼント
    ]

    else:
        return False
    return any(x1 <= px <= x2 and y1 <= py <= y2 for x1, y1, x2, y2 in collision_areas)

def check_near(x, y, obj):
    px, py = x + player_size // 2, y + player_size // 2
    area = {
        # room1
        "nemo_bag": (85, 0, 120, 70),
        "reizouko": (0, 0, 45, 80),
        "right_shelf": (215, 0, 250, 70),
        "lamp": (225, 110, 255, 205),
        "aircleaner": (200, 140, 235, 205),
        "tv_shelf": (130, 70, 180, 98),
        "tsumetogi": (30, 115, 90, 175),
        "pc": (125, 110, 145, 152),
        "table": (170, 110, 210, 152),
        "gomibako": (95, 155, 215, 205),
        "bed_door": (45, 0, 85, 60),  # 🛌 冷蔵庫右隔の扉
        # bedroom
        "bat": (171, 10, 185, 55),  # バット
        "painting": (230, 10, 250, 55),  # 絵画
        "box": (208, 113, 250, 200),  # 段ボール
        "fire": (165, 130, 195, 170),  # 焚火
        "shelf1_1": (0, 0, 50, 68),  # クリスマスツリー
        "shelf1_2": (53, 0, 85, 63),  # 雪だるま
        "shelf1_3": (85, 0, 110, 63),  # くま
        "shelf1_4": (110, 0, 135, 63),  # おみくじ
        "shelf1_5": (143, 0, 160, 63),  # さくらんぼ
        "shelf2_1": (143, 67, 160, 120),  # じゅう
        "shelf2_2": (110, 67, 135, 120),  # ワットソン
        "shelf2_3": (85, 67, 110, 120),  # ゴルフ
        "shelf2_4": (55, 67, 80, 120),  # もみじ
        "shelf2_5": (25, 67, 50, 120),  # 温泉
        "shelf2_6": (0, 67, 25, 120),  # ラーメン
        "shelf3_1": (110, 125, 160, 170),  # ぼうし
        "shelf3_2": (85, 125, 110, 170),  # 麻雀
        "shelf3_3": (60, 125, 85, 170),  # クレープ
        "shelf3_4": (25, 125, 50, 170),  # 競馬
        "shelf3_5": (0, 125, 25, 175),  # さくら
        "exit_door": (195, 0, 230, 60),  # 🏠 寝室から出る右上ドア
        "genkan_door": (0, 140, 20, 160),
        # genkan
        "genkan_door_exit": (115, 0, 155, 85),  # 🚪 玄関の上のドア
        "present": (100, 80, 155, 130),  # 🚪 
        "cat": (30, 90, 72, 110),           # 🐱 左下の猫
        "room2_door": (40, 180, 90, 200),    # 🎮 左下の扉風エリア
        #room2
        "room2_exit_door": (80, 0, 140, 80),  # 🎮 room2の上のドア（戻り口）
        "room2_obj1": (95, 60, 200, 145),     # 🎂 ケーキテーブル
        "room2_obj2": (190, 0, 255, 95),      # 🎁 プレゼント山
        "room2_food_table": (0, 148, 255, 200),     # 🍴 食事台
        "room2_dishes": (180, 143, 210, 200),       # 🍽️ 片づけ
        "room2_flower": (220, 120, 255, 200),       # 💐 花
        "room2_kin": (225, 0, 255, 115),            # 👑 kin
        "room2_pink": (0, 0, 76, 86),               # 🩷 ピンクのキャラ
        

    }.get(obj, (0, 0, 0, 0))
    x1, y1, x2, y2 = area
    return x1 <= px <= x2 and y1 <= py <= y2

def draw():
    pyxel.cls(0)
    pyxel.blt(0, 0, 0, 0, 0, 255, 200, 0)
    u_table = {"front": 0, "left": 32, "right": 64, "back": 96}
    u = u_table[player_dir]
    pyxel.blt(player_x, player_y, 1, u, 0, 32, 32, 0)

    if show_message:
        pyxel.blt(17, 150, 2, 0, 0, 220, 35, 0)
        msg_table = {
            # room1
            "nemo_bag": "いつもここに物が置いてある...",
            "reizouko": "冷蔵庫の中は夢と希望と賞味期限切れの食料...",
            "right_shelf": "黄色の花が飾られてる！",
            "lamp": "この間接照明ついてるとこみたことないな",
            "aircleaner": "空気清潔機くん、今日もいい仕事してるね",
            "tv_shelf": "手紙が届くお店が放送されてる！",
            "tsumetogi": "ガリガリ...え？私が使ってるわけじゃないよ？？",
            "table": "マックに寄るんだ！",
            "pc": "ゲームをしてる自分が映ってる・・",
            "gomibako": "あ！パンがはいってる！モグッ・・・ウッおなかが・・・",
            "room_open": "寝室に入れるようになったようだ！",
            "bed_door": "寝室にいってみよう！",
            "go_genkan": "玄関にいこう！",
            "cat": "きんきんかわいいね！",
            "room2_unlock": "ゲーム部屋にいけるようになったようだ！",
            "go_room2": "ゲーム部屋にいってみよう！",


            # bedroom
            "bat": "バッティングセンターに行こうかな！",
            "painting": "もうパズルは勘弁",
            "box": "もともと寝室にあったものが押し込まれてる・・・",
            "fire": "マシュマロ焼きたい・・・",
            "shelf1_1": "クリスマスツリー！きれいだね！","shelf1_2": "スノーボードしにいきたいな！",
            "shelf1_3": "誕生日にやった熊アート！かわいい！","shelf1_4": "ガシャガシャ・・今回は大吉だ！","shelf1_5": "さくらんぼ狩りにいきたいな！",
            "shelf2_1": "これは・・・モザンビーク！！","shelf2_2": "たくさんAPEXするぞ！","shelf2_3": "フォーム早くなんとかしないと・・・",
            "shelf2_4": "もみじ狩りキレイだ！","shelf2_5": "サウナ！キマりたい","shelf2_6": "ラーメン開拓！",
            "shelf3_1": "ニューエラの帽子可愛くてお気に入り！","shelf3_2": "じゃん魂！",
            "shelf3_3": "ジラフクレープ!クリームチーズブルーベリークリーム！","shelf3_4": "安田記念で賢者タイム","shelf3_5": "今年のさくらキレイだったな",
            "exit_to_room1": "リビングに戻ろう！",
            "genkan_open": "玄関に行けるようになった！",

            #genkan
            "present": "黒い箱だ！",
            "genkan_door_exit": "リビングに戻ろう！",

            #game
            "room2_exit_door": "リビングにもどろう！",
            "room2_obj1": "3段ケーキ！？誕生日ってレベルじゃねぇ！",
            "room2_obj2": "プレゼントが山のように積まれてる！どれから開けよう？",
            "room2_food_table": "フルコース！？バースデーパーティーってすごい…！",
            "room2_dishes": "もう片づけられてる…たくさん食べたなぁ。",
            "room2_flower": "お花も飾られてる！",
            "room2_kin": "あれ？手紙をもってる・・",
            "room2_pink": "巨大ぷにぷにがいる！…ふれたら気持ちよさそう…",
        }
        pyxel.text(22, 160, msg_table.get(show_message, ""), 7, font)

    if show_letter:
        pyxel.blt((255 - 200) // 2, (200 - 141) // 2, 2, 0, 110, 200, 141, 0)
    if cat_visible and current_room == "room1":
        pyxel.blt(40, 100, 2, 0, 64, 32, 32, 0)  # 🐱 つめとぎの上に表示
pyxel.run(update, draw)
