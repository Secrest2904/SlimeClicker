import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageSequence
import os

# Constants
SLIME_TIERS = ["clear", "water", "rock", "fire", "grass", "ice", "magma", "space"]
UPGRADES = ["grass_patch", "well", "rock_pile", "bonfire", "forest", "glacier", "volcano", "planet"]
UPGRADE_COSTS = {
    "grass_patch": 16,
    "well": 128,
    "rock_pile": 1024,
    "bonfire": 8192,
    "forest": 65536,
    "glacier": 524288,
    "volcano": 4194304,
    "planet": 33554432
}
BASE_GPS = {
    "grass_patch": 1,
    "well": 8,
    "rock_pile": 64,
    "bonfire": 512,
    "forest": 4096,
    "glacier": 32768,
    "volcano": 262144,
    "planet": 2097152
}
PRESTIGE_COSTS = {
    0: 4000,
    1: 16000,
    2: 64000,
    3: 256000,
    4: 1024000,
    5: 4096000,
    6: 16384000,
    7: 65536000
}
color = '#7055a1'

class SlimeClickerGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Slime Farm Clicker")
        self.root.geometry("1000x600")
        self.current_slime = None
        self.current_gif_index = 0


        self.gelatin = 0
        self.slime_tier = 0
        self.upgrades = {name: 0 for name in UPGRADE_COSTS}

        self.slime_images = {}
        self.slime_gifs = {}
        self.upgrade_images = {}

        self.load_images()
        self.setup_ui()
        self.update_ui()
        self.auto_generate_gelatin()

    def calculate_gps(self):
        total = 0
        for i, name in enumerate(UPGRADES):
            count = self.upgrades[name]
            base = BASE_GPS[name]
            tier_bonus = 1
            if i <= self.slime_tier:
                tier_bonus = self.slime_tier - i + 2 if self.slime_tier - i + 1 >= 0 else 1
            total += count * base * tier_bonus
        return total

    def auto_generate_gelatin(self):
        gps = self.calculate_gps()
        self.gelatin += int(gps)
        self.update_ui()
        self.root.after(1000, self.auto_generate_gelatin)

    def load_images(self):
        base_path = os.path.dirname(os.path.abspath(__file__))

        for tier in SLIME_TIERS:
            filename_png = os.path.join(base_path, "sprites", "slimes", f"{tier}.png")
            filename_gif = os.path.join(base_path, "sprites", "slimes", f"{tier}.gif")

            try:
                if os.path.exists(filename_gif):
                    gif = Image.open(filename_gif)
                    frames = [ImageTk.PhotoImage(frame.resize((256, 256))) for frame in ImageSequence.Iterator(gif)]
                    self.slime_gifs[tier] = frames
                    print(f"[✓] Loaded GIF for {tier}")
                    continue
            except Exception as e:
                print(f"[✗] Failed to load GIF for {tier}: {e}")

            if os.path.exists(filename_png):
                try:
                    img = Image.open(filename_png).resize((200, 256))
                    self.slime_images[tier] = ImageTk.PhotoImage(img)
                    print(f"[✓] Loaded PNG for {tier}")
                except Exception as e:
                    print(f"[✗] Failed to load PNG for {tier}: {e}")
            else:
                print(f"[!] No image found for {tier}")
        for name in UPGRADES:
            upgrade_path = os.path.join(base_path, "sprites", "upgrades", f"{name}.png")
            if os.path.exists(upgrade_path):
                try:
                    img = Image.open(upgrade_path).copy().resize((32, 32))
                    self.upgrade_images[name] = ImageTk.PhotoImage(img)
                    print(f"[✓] Loaded upgrade image: {name}")
                except Exception as e:
                    print(f"[✗] Failed to load upgrade {name}: {e}")
            else:
                print(f"[!] Upgrade image not found for: {name}")

    def setup_ui(self):
        self.left_frame = tk.Frame(self.root, width=500, bg=color)
        self.left_frame.pack(side="left", fill="y")
        self.left_frame.pack_propagate(False)

        self.slime_label = tk.Label(self.left_frame, image=None, bg=color)
        self.slime_label.pack(pady=20)
        self.slime_label.bind("<Button-1>", self.on_slime_click)

        self.gelatin_label = tk.Label(self.left_frame, text="Gelatin: 0", font=("Arial", 24), fg="White", bg=color)
        self.gelatin_label.pack(pady=10)

        self.prestige_progress = tk.Label(self.left_frame, text="Slime Tier: 1/8", font=("Arial", 12), fg="White", bg=color)
        self.prestige_progress.pack(pady=5)

        self.note_label = tk.Label(self.left_frame, text="*Gelatin gets set to 0 on prestige*", fg="#c9c9c9", bg=color, font=("Arial", 10))
        self.note_label.pack(pady=5)

        self.right_frame = tk.Frame(self.root, width=700, bg="#2a9fd1")
        self.right_frame.pack(side="right", fill="both", expand=True)

        self.prestige_button = tk.Button(self.right_frame, text="Prestige to Next Slime", command=self.prestige, font=("Arial", 14), bg="gold")
        self.prestige_button.pack(pady=10)

        self.upgrade_frames = []
        for i, upgrade in enumerate(UPGRADES):
            frame = tk.Frame(self.right_frame, bg="#222")
            frame.pack(pady=4, fill="x", padx=20)

            img_label = tk.Label(frame, image=self.upgrade_images.get(upgrade), bg="#222")
            img_label.pack(side="left", padx=5)

            name_label = tk.Label(frame, text=upgrade.replace("_", " ").title(), font=("Arial", 12), bg="#222", fg="white")
            name_label.pack(side="left", padx=10)

            multiplier_label = tk.Label(frame, text="", font=("Arial", 10), bg="#222", fg="yellow")
            multiplier_label.pack(side="right", padx=5)

            count_label = tk.Label(frame, text=f"x{self.upgrades[upgrade]}", font=("Arial", 10), bg="#222", fg="lightgray")
            count_label.pack(side="right", padx=5)

            btn = tk.Button(frame, text=f"Buy ({UPGRADE_COSTS[upgrade]})", command=lambda u=upgrade: self.buy_upgrade(u))
            btn.pack(side="right")

            self.upgrade_frames.append((upgrade, name_label, btn, count_label, multiplier_label))

    def on_slime_click(self, event=None):
        self.gelatin += 1
        self.update_ui()

    def buy_upgrade(self, name):
        cost = int(UPGRADE_COSTS[name] * (1.05 ** self.upgrades[name]))
        if self.gelatin >= cost:
            self.gelatin -= cost
            self.upgrades[name] += 1
            self.update_ui()
        else:
            messagebox.showinfo("Not enough gelatin", "You need more gelatin for this upgrade.")

    def prestige(self):
        if self.slime_tier < len(SLIME_TIERS) - 1:
            required = PRESTIGE_COSTS.get(self.slime_tier, float('inf'))
            if self.gelatin >= required:
                self.slime_tier += 1
                self.gelatin = 0
                for name in self.upgrades:
                    self.upgrades[name] = 0
                self.update_ui()
            else:
                messagebox.showinfo("Cannot Prestige", f"You need {required} gelatin to prestige.")
        else:
            messagebox.showinfo("Max Tier", "You’ve reached the final slime!")

    def update_ui(self):
        tier_name = SLIME_TIERS[self.slime_tier]

        if tier_name in self.slime_gifs:
            if self.current_slime != tier_name:
                self.current_slime = tier_name
                self.current_gif_index = 0
                self.animate_gif(self.slime_gifs[tier_name], 0)
        else:
            img = self.slime_images.get(tier_name)
            self.slime_label.config(image=img)
            self.slime_label.image = img
            self.current_slime = None

        gps = self.calculate_gps()
        self.gelatin_label.config(text=f"Gelatin: {self.gelatin} (+{gps}/sec)")
        self.prestige_progress.config(text=f"Slime Tier: {self.slime_tier + 1}/8")

        for i, (upgrade, _, btn, count_label, multiplier_label) in enumerate(self.upgrade_frames):
            cost = int(UPGRADE_COSTS[upgrade] * (1.05 ** self.upgrades[upgrade]))
            btn.config(text=f"Buy ({cost})")
            count_label.config(text=f"x{self.upgrades[upgrade]}")

            if i <= self.slime_tier:
                multiplier = self.slime_tier - i + 2 if self.slime_tier - i + 1 >= 0 else 1
                multiplier_label.config(text=f"x{multiplier}")
            else:
                multiplier_label.config(text="")

    def animate_gif(self, frames, index):
        if self.current_slime not in self.slime_gifs:
            return

        frame = frames[index]
        self.slime_label.config(image=frame)
        self.slime_label.image = frame
        self.root.after(100, lambda: self.animate_gif(frames, (index + 1) % len(frames)))


# Run the game
if __name__ == "__main__":
    root = tk.Tk()
    app = SlimeClickerGame(root)
    root.mainloop()
