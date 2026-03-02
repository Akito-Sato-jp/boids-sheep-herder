import tkinter as tk
from PIL import Image, ImageTk, ImageOps
import random
import time
import math
import os
import sys

# =====================
# PyInstaller用パス解決関数
# =====================
def resource_path(relative_path):
    """ リソースファイルへの絶対パスを取得する（exe化対応） """
    try:
        # PyInstallerの一時フォルダパス
        base_path = sys._MEIPASS
    except Exception:
        # 通常実行時のパス
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# --- 設定 ---
WIDTH, HEIGHT = 800, 600
SHEEP_COUNT = 15
PLAYER_SPEED = 7
SHEEP_SPEED = 4
WANDER_SPEED = 1.2
DETECTION_DIST = 140
GOAL_DIST = 60
FPS = 60

# 群れアルゴリズムの設定
SEPARATION_DIST = 35
COHESION_DIST = 100
FLOCK_WEIGHT = 0.05
TURN_SPEED = 0.15

# ゲーム状態
STATE_TITLE = "TITLE"
STATE_PLAYING = "PLAYING"
STATE_CLEAR = "CLEAR"

class SheepGame:
    def __init__(self, root):
        self.root = root
        self.root.title("羊追いゲーム: FOREST SURVIVOR")
        
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#2d5a27", highlightthickness=0)
        self.canvas.pack()

        self.assets = self.load_assets()
        self.state = STATE_TITLE
        
        # キー入力のバインド
        self.root.bind("<space>", self.on_space)
        self.root.bind("<r>", self.on_r_key)
        self.root.bind("R", self.on_r_key)
        self.mouse_pos = [WIDTH//2, HEIGHT//2]
        self.root.bind("<Motion>", self.mouse_move)
        
        self.sheeps = []
        self.dog_id = None
        self.info_text = None
        
        self.update()

    def load_assets(self):
        """ resource_pathを使用して画像をロードする """
        files = {
            "bg": ("grass.jpg", (WIDTH, HEIGHT)),
            "dog": ("dog.png", (40, 40)),
            "sheep": ("sheep.png", (35, 30))
        }
        
        processed = {}
        try:
            for key, (name, size) in files.items():
                path = resource_path(name)
                if os.path.exists(path):
                    img = Image.open(path).convert("RGBA")
                    img = img.resize(size, Image.Resampling.LANCZOS)
                    if key == "sheep":
                        processed["sheep_r"] = ImageTk.PhotoImage(img)
                        processed["sheep_l"] = ImageTk.PhotoImage(ImageOps.mirror(img))
                    elif key == "dog":
                        processed["dog_r"] = ImageTk.PhotoImage(img)
                        processed["dog_l"] = ImageTk.PhotoImage(ImageOps.mirror(img))
                    else:
                        processed[key] = ImageTk.PhotoImage(img)
                else:
                    print(f"警告: ファイルが見つかりません: {path}")
                    processed[key] = None
            return processed
        except Exception as e:
            print(f"画像読み込みエラー: {e}")
            return {}

    def show_title_screen(self):
        self.canvas.delete("all")
        if self.assets.get("bg"):
            self.canvas.create_image(0, 0, image=self.assets["bg"], anchor="nw")
        
        self.canvas.create_text(WIDTH//2, HEIGHT//2 - 60, text="SHEEP HERDING", 
                               fill="white", font=("Arial", 48, "bold"), tags="ui")
        self.canvas.create_text(WIDTH//2, HEIGHT//2 + 20, text="Lead all sheep to the goal!", 
                               fill="#e0e0e0", font=("Arial", 18), tags="ui")
        self.canvas.create_text(WIDTH//2, HEIGHT//2 + 100, text="Press [ SPACE ] to Start", 
                               fill="yellow", font=("Arial", 24, "bold"), tags="ui")

    def setup_game(self):
        self.canvas.delete("all")
        if self.assets.get("bg"):
            self.canvas.create_image(0, 0, image=self.assets["bg"], anchor="nw")

        # ゴールエリア
        self.goal_x, self.goal_y = WIDTH - 80, 80
        self.canvas.create_rectangle(self.goal_x-55, self.goal_y-55, self.goal_x+55, self.goal_y+55, 
                                     outline="white", width=2, dash=(5,5))

        # 犬（プレイヤー）
        img_dog = self.assets.get("dog_r")
        if img_dog:
            self.dog_id = self.canvas.create_image(WIDTH//2, HEIGHT//2, image=img_dog)
        else:
            self.dog_id = self.canvas.create_oval(WIDTH//2-15, HEIGHT//2-15, WIDTH//2+15, HEIGHT//2+15, fill="#8B4513")

        # 羊
        self.sheeps = []
        for _ in range(SHEEP_COUNT):
            sx, sy = random.randint(50, 300), random.randint(100, 500)
            img_s = self.assets.get("sheep_r")
            s_id = self.canvas.create_image(sx, sy, image=img_s) if img_s else \
                   self.canvas.create_oval(sx-12, sy-12, sx+12, sy+12, fill="white", outline="gray")
                
            self.sheeps.append({
                "id": s_id, "x": sx, "y": sy,
                "angle": random.uniform(0, 2 * math.pi),
                "walking": False,
                "dir": "r"
            })

        self.info_text = self.canvas.create_text(20, 30, anchor="nw", fill="white", font=("Arial", 14, "bold"))
        self.start_time = time.time()

    def mouse_move(self, event):
        self.mouse_pos = [event.x, event.y]

    def on_space(self, event):
        if self.state == STATE_TITLE:
            self.setup_game()
            self.state = STATE_PLAYING

    def on_r_key(self, event):
        if self.state == STATE_CLEAR:
            self.state = STATE_TITLE

    def update(self):
        if self.state == STATE_TITLE:
            self.show_title_screen()
        elif self.state == STATE_PLAYING:
            self.update_game_logic()
        self.root.after(1000 // FPS, self.update)

    def update_game_logic(self):
        # 犬の移動
        cur_dog = self.canvas.coords(self.dog_id)
        dx_dog = self.mouse_pos[0] - cur_dog[0]
        dy_dog = self.mouse_pos[1] - cur_dog[1]
        dist_dog = math.hypot(dx_dog, dy_dog)
        
        if dist_dog > 5:
            vx_d, vy_d = (dx_dog/dist_dog)*PLAYER_SPEED, (dy_dog/dist_dog)*PLAYER_SPEED
            self.canvas.move(self.dog_id, vx_d, vy_d)
            if self.assets.get("dog_l"):
                self.canvas.itemconfig(self.dog_id, image=self.assets["dog_r"] if vx_d > 0 else self.assets["dog_l"])

        dog_coords = self.canvas.coords(self.dog_id)
        if not dog_coords: return
        dog_x, dog_y = dog_coords[0:2]

        next_sheeps = []
        for s in self.sheeps:
            dist_to_dog = math.hypot(s["x"] - dog_x, s["y"] - dog_y)
            desired_vx, desired_vy = 0, 0
            current_speed = 0

            if dist_to_dog < DETECTION_DIST:
                esc_ang = math.atan2(s["y"] - dog_y, s["x"] - dog_x)
                desired_vx, desired_vy = math.cos(esc_ang), math.sin(esc_ang)
                current_speed = SHEEP_SPEED
            else:
                if random.random() < 0.02: s["walking"] = not s["walking"]
                if s["walking"]:
                    s["angle"] += random.uniform(-0.1, 0.1)
                    desired_vx, desired_vy = math.cos(s["angle"]), math.sin(s["angle"])
                    current_speed = WANDER_SPEED

            sep_x, sep_y, coh_x, coh_y, count = 0, 0, 0, 0, 0
            for other in self.sheeps:
                if other == s: continue
                d = math.hypot(s["x"] - other["x"], s["y"] - other["y"])
                if d < SEPARATION_DIST:
                    sep_x += (s["x"] - other["x"]); sep_y += (s["y"] - other["y"])
                elif d < COHESION_DIST:
                    coh_x += other["x"]; coh_y += other["y"]; count += 1
            
            total_vx = desired_vx * current_speed + sep_x * 0.2
            total_vy = desired_vy * current_speed + sep_y * 0.2
            if count > 0:
                total_vx += ((coh_x/count) - s["x"]) * FLOCK_WEIGHT
                total_vy += ((coh_y/count) - s["y"]) * FLOCK_WEIGHT

            if total_vx != 0 or total_vy != 0:
                target_angle = math.atan2(total_vy, total_vx)
                diff = (target_angle - s["angle"] + math.pi) % (2 * math.pi) - math.pi
                s["angle"] += diff * TURN_SPEED
                actual_speed = min(math.hypot(total_vx, total_vy), SHEEP_SPEED)
                s["x"] += math.cos(s["angle"]) * actual_speed
                s["y"] += math.sin(s["angle"]) * actual_speed

            vx_facing = math.cos(s["angle"])
            if abs(vx_facing) > 0.2:
                new_dir = "r" if vx_facing > 0 else "l"
                if new_dir != s["dir"]:
                    s["dir"] = new_dir
                    if self.assets.get(f"sheep_{new_dir}"):
                        self.canvas.itemconfig(s["id"], image=self.assets[f"sheep_{new_dir}"])

            s["x"] = max(25, min(WIDTH-25, s["x"]))
            s["y"] = max(25, min(HEIGHT-25, s["y"]))
            self.canvas.coords(s["id"], s["x"], s["y"])

            if math.hypot(s["x"] - self.goal_x, s["y"] - self.goal_y) < GOAL_DIST:
                self.canvas.delete(s["id"])
            else:
                next_sheeps.append(s)

        self.sheeps = next_sheeps
        elapsed = int(time.time() - self.start_time)
        self.canvas.itemconfig(self.info_text, text=f"SHEEP: {len(self.sheeps)} | TIME: {elapsed}s")

        if not self.sheeps:
            self.state = STATE_CLEAR
            self.canvas.create_text(WIDTH//2, HEIGHT//2, text="MISSION COMPLETE!", fill="yellow", font=("Arial", 48, "bold"))
            self.canvas.create_text(WIDTH//2, HEIGHT//2 + 60, text=f"Clear Time: {elapsed} seconds", fill="white", font=("Arial", 20))
            self.canvas.create_text(WIDTH//2, HEIGHT//2 + 120, text="Press [ R ] to Title", fill="#ccc", font=("Arial", 16))

if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(False, False)
    game = SheepGame(root)
    root.mainloop()