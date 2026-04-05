"""
Dragon Runner — Dynasty Edition
================================
Eight Chinese dynasties, each with a unique background and escalating
challenge frequency. Collect powerup coins to boost your scores.
Touch an obstacle to trigger a crisis scenario popup.

Scores: Military · Authority · Prosperity · Descendants  (all start at 8)
Any score < 2 = Dynasty falls. Complete all 8 dynasties to win.

Controls:
  SPACE  — jump (parabolic arc)
  SPACE/CLICK — advance transition screens
  R      — restart from beginning
  ESC    — quit

Assets needed (same folder as this script):
  dragon.png  famine.png  rebellious_general.png  devious_eunuch.png
"""

import sys, os, math, random, time
import asyncio # <--- ADD THIS LINE
import pygame

# ─────────────────────────────────────────────────────────────────────────────
# Asset paths & validation
# ─────────────────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
def asset(name): return os.path.join(SCRIPT_DIR, name)

REQUIRED = ["dragon.png","famine.png","rebellious_general.png","devious_eunuch.png"]
missing  = [f for f in REQUIRED if not os.path.exists(asset(f))]
if missing:
    print("ERROR: Missing image files (place them next to this script):")
    for m in missing: print(f"  {m}")
    sys.exit(1)

# ─────────────────────────────────────────────────────────────────────────────
# Window / layout
# ─────────────────────────────────────────────────────────────────────────────
W, H   = 1100, 500
FPS    = 60
GROUND = H - 90

# ─────────────────────────────────────────────────────────────────────────────
# Dynasty definitions
# ─────────────────────────────────────────────────────────────────────────────
DYNASTIES = [
    {
        "name": "Xia Dynasty", "years": "c. 2070-1600 BC",
        "blurb": (
            "Founded by Yu the Great, first dynasty in Chinese history.\n"
            "Known for flood control, the beginnings of the dynastic\n"
            "system, and early Bronze Age civilization."
        ),
        "challenges": 4,
        "sky_top":   ( 30,  55,  90), "sky_bot":  ( 80, 120, 160),
        "ground":    ( 55, 100,  45), "mountain": ( 20,  40,  70),
        "cloud":     ( 90, 130, 180),
        "tech_powerup": "Agriculture",  "talent_name": "King Yu",
    },
    {
        "name": "Shang Dynasty", "years": "c. 1600-1046 BC",
        "blurb": (
            "First dynasty with written records -- oracle bones.\n"
            "Advanced bronze metallurgy, organised cities,\n"
            "and the foundations of Chinese writing."
        ),
        "challenges": 6,
        "sky_top":   ( 55,  30,  10), "sky_bot":  (110,  70,  20),
        "ground":    ( 80,  90,  30), "mountain": ( 40,  20,   8),
        "cloud":     (160, 120,  60),
        "tech_powerup": "Oracle Bones",  "talent_name": "King Tang",
    },
    {
        "name": "Zhou Dynasty", "years": "c. 1046-256 BC",
        "blurb": (
            "The longest dynasty -- introduced the Mandate of Heaven.\n"
            "Birthplace of Confucianism and Daoism.\n"
            "Warring States produced China's greatest philosophers."
        ),
        "challenges": 8,
        "sky_top":   ( 20,  40,  20), "sky_bot":  ( 50,  90,  40),
        "ground":    ( 40,  80,  30), "mountain": ( 15,  35,  15),
        "cloud":     ( 70, 110,  60),
        "tech_powerup": "Crossbow",  "talent_name": "King Wen Wu",
    },
    {
        "name": "Han Dynasty", "years": "206 BC - 220 AD",
        "blurb": (
            "A golden age -- Confucianism as state ideology.\n"
            "Opened the Silk Road, advanced science and governance.\n"
            "So influential that Chinese people call themselves 'Han'."
        ),
        "challenges": 10,
        "sky_top":   ( 60,  20,  20), "sky_bot":  (130,  50,  30),
        "ground":    ( 90,  60,  20), "mountain": ( 45,  15,  10),
        "cloud":     (190, 120,  70),
        "tech_powerup": "Paper",  "talent_name": "Liu Bang",
    },
    {
        "name": "Tang Dynasty", "years": "618-907 AD",
        "blurb": (
            "A high point in arts, culture, and international trade.\n"
            "Cosmopolitan capital Chang'an was the world's largest city.\n"
            "Sophisticated civil service exams, poetry, and Buddhism."
        ),
        "challenges": 12,
        "sky_top":   ( 15,  15,  50), "sky_bot":  ( 40,  35, 110),
        "ground":    ( 30,  75,  80), "mountain": ( 10,  10,  40),
        "cloud":     ( 60,  80, 160),
        "tech_powerup": "Gunpowder",  "talent_name": "Li Shimin",
    },
    {
        "name": "Song Dynasty", "years": "960-1279 AD",
        "blurb": (
            "Era of economic and technological revolution.\n"
            "Invented paper money and advanced gunpowder weaponry.\n"
            "Faced relentless pressure from Jurchen and Mongol invaders."
        ),
        "challenges": 14,
        "sky_top":   ( 45,  45,  45), "sky_bot":  (100, 100,  90),
        "ground":    ( 60,  80,  50), "mountain": ( 30,  30,  30),
        "cloud":     (140, 140, 130),
        "tech_powerup": "Printing Press",  "talent_name": "Taizu",
    },
    {
        "name": "Ming Dynasty", "years": "1368-1644 AD",
        "blurb": (
            "Native Chinese power restored after Mongol rule.\n"
            "Built the Great Wall, launched Zheng He's epic voyages.\n"
            "A flourishing of culture, porcelain, and drama."
        ),
        "challenges": 16,
        "sky_top":   ( 40,  10,  10), "sky_bot":  ( 90,  30,  20),
        "ground":    ( 70,  45,  20), "mountain": ( 30,   8,   8),
        "cloud":     (160,  90,  60),
        "tech_powerup": "Toothbrush",  "talent_name": "Zhu Yuanzhang",
    },
    {
        "name": "Qing Dynasty", "years": "1644-1912 AD",
        "blurb": (
            "The final dynasty, led by the Manchu people.\n"
            "Expanded China to its greatest territorial extent.\n"
            "Ended with internal unrest and foreign encroachment."
        ),
        "challenges": 18,
        "sky_top":   ( 10,  10,  30), "sky_bot":  ( 30,  30,  70),
        "ground":    ( 35,  55,  60), "mountain": (  8,   8,  25),
        "cloud":     ( 60,  70, 110),
        "tech_powerup": "Early Machine Gun",  "talent_name": "Yongle",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# Challenge data
# ─────────────────────────────────────────────────────────────────────────────
CHALLENGES = {
    "famine": {
        "title":    "FAMINE",
        "image":    "famine.png",
        "scenario": (
            "A great famine has struck the land.\n"
            "The granaries are empty, the people cry out.\n"
            "What do you do?"
        ),
        "options": [
            {
                "text":    "Pray.",
                "subtitle":"Hold grand ceremonies and beseech the heavens.",
                "effects": {"Prosperity": -0.60, "Military": -0.30, "Authority": -0.20},
            },
            {
                "text":    "Ignore.",
                "subtitle":"The strong survive. Weakness is culled.",
                "effects": {"Prosperity": -0.50, "Military": -0.30, "Authority": -0.60},
            },
        ],
    },
    "rebellious_general": {
        "title":    "REBELLIOUS GENERAL",
        "image":    "rebellious_general.png",
        "scenario": (
            "Your most powerful general has revolted!\n"
            "He leads your finest troops and has fortified\n"
            "a distant city as his own domain. What do you do?"
        ),
        "options": [
            {
                "text":    "War! Attack his stronghold!",
                "subtitle":"Crush the traitor. Make an example.",
                "effects": {"Prosperity": -0.20, "Military": -0.60, "Authority": -0.60},
            },
            {
                "text":    "Bribe him with treasure.",
                "subtitle":"We can reach an understanding.",
                "effects": {"Military": -0.40, "Authority": -0.60},
            },
        ],
    },
    "devious_eunuch": {
        "title":    "DEVIOUS EUNUCH",
        "image":    "devious_eunuch.png",
        "scenario": (
            "Your most trusted court eunuch is secretly corrupt.\n"
            "He weaves a political faction in the shadows -- yet\n"
            "he alone keeps the bureaucracy running. What do you do?"
        ),
        "options": [
            {
                "text":    "Off with his head.",
                "subtitle":"No treachery shall fester in this court.",
                "effects": {"Military": -0.20, "Authority": -0.30},
            },
            {
                "text":    "Turn a blind eye.",
                "subtitle":"Stability above all. For now.",
                "effects": {"Prosperity": -0.10, "Military": -0.30, "Authority": -0.30},
            },
        ],
    },
}
CHALLENGE_KEYS = list(CHALLENGES.keys())

# ─────────────────────────────────────────────────────────────────────────────
# Powerup types
# ─────────────────────────────────────────────────────────────────────────────
POWERUP_TYPES = {
    "tech":    {"color": (255,215,  0), "effects": {"Prosperity":+0.10,"Military":+0.20}},
    "harvest": {"color": ( 80,200, 80), "effects": {"Prosperity":+0.30}},
    "talent":  {"color": (100,180,255), "effects": {"Prosperity":+0.10,"Military":+0.10,
                                                     "Authority":+0.10,"Descendants":+0.10}},
}

# ─────────────────────────────────────────────────────────────────────────────
# Colour constants
# ─────────────────────────────────────────────────────────────────────────────
C_WHITE = (245, 235, 210)
C_GOLD  = (210, 175,  55)
C_RED   = (180,  35,  35)
SCORE_COLORS = {
    "Military":    (200,  60,  60),
    "Authority":   (200, 160,  40),
    "Prosperity":  ( 60, 180,  80),
    "Descendants": (100, 150, 220),
}

# ─────────────────────────────────────────────────────────────────────────────
# Utility
# ─────────────────────────────────────────────────────────────────────────────
def lerp3(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i] + (b[i]-a[i])*t) for i in range(3))

def load_img(fname, scale=None):
    surf = pygame.image.load(asset(fname)).convert_alpha()
    if scale:
        surf = pygame.transform.smoothscale(surf, scale)
    return surf

def draw_text_wrapped(surface, text, font, color, rect, line_spacing=6):
    lines   = text.split("\n")
    total_h = len(lines) * (font.get_height() + line_spacing)
    y       = rect.top + (rect.height - total_h) // 2
    for line in lines:
        s = font.render(line, True, color)
        surface.blit(s, (rect.left + (rect.width - s.get_width())//2, y))
        y += font.get_height() + line_spacing

def rounded_rect_surf(w, h, r, color):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(surf,   color, (r, 0, w-2*r, h))
    pygame.draw.rect(surf,   color, (0, r, w, h-2*r))
    for cx, cy in [(r,r),(w-r,r),(r,h-r),(w-r,h-r)]:
        pygame.draw.circle(surf, color, (cx,cy), r)
    return surf

def blit_center(surface, s, cy):
    surface.blit(s, (W//2 - s.get_width()//2, cy))

# ─────────────────────────────────────────────────────────────────────────────
# Dragon
# ─────────────────────────────────────────────────────────────────────────────
class Dragon:
    JUMP_VY = -18
    GRAVITY = 0.7

    def __init__(self, frames):
        self.frames    = frames
        self.x         = 140
        self.y         = float(GROUND)
        self.vy        = 0.0
        self.on_ground = True
        self.frame     = 0
        self.frame_t   = 0
        self.flash_t   = 0

    @property
    def rect(self):
        img = self.frames[int(self.frame)]
        return pygame.Rect(self.x, int(self.y)-img.get_height(),
                           img.get_width(), img.get_height())

    @property
    def hitbox(self):
        r = self.rect
        return pygame.Rect(r.x+12, r.y+10, r.width-24, r.height-14)

    def jump(self):
        if self.on_ground:
            self.vy, self.on_ground = self.JUMP_VY, False

    def update(self):
        if not self.on_ground:
            self.vy += self.GRAVITY
            self.y  += self.vy
            if self.y >= GROUND:
                self.y, self.vy, self.on_ground = float(GROUND), 0.0, True
        self.frame_t += 1
        if self.on_ground and self.frame_t >= 8:
            self.frame, self.frame_t = (self.frame+1) % len(self.frames), 0
        elif not self.on_ground:
            self.frame = 0
        if self.flash_t > 0:
            self.flash_t -= 1

    def draw(self, surface):
        img = self.frames[int(self.frame)].copy()
        if self.flash_t > 0 and (self.flash_t//3) % 2 == 0:
            fl = pygame.Surface(img.get_size(), pygame.SRCALPHA)
            fl.fill((255,60,60,120))
            img.blit(fl, (0,0))
        surface.blit(img, self.rect.topleft)

# ─────────────────────────────────────────────────────────────────────────────
# Obstacle
# ─────────────────────────────────────────────────────────────────────────────
class Obstacle:
    BASE_SPEED = 5.0

    def __init__(self, key, image, x):
        self.key, self.image, self.x, self.triggered = key, image, float(x), False

    @property
    def rect(self):
        return pygame.Rect(int(self.x), GROUND-self.image.get_height(),
                           self.image.get_width(), self.image.get_height())
    @property
    def hitbox(self):
        r = self.rect
        return pygame.Rect(r.x+6, r.y+6, r.width-12, r.height-6)

    def update(self, speed_mult=1.0):
        self.x -= self.BASE_SPEED * speed_mult

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)
        sh = pygame.Surface((self.image.get_width(), 8), pygame.SRCALPHA)
        sh.fill((0,0,0,50))
        surface.blit(sh, (int(self.x), GROUND))

# ─────────────────────────────────────────────────────────────────────────────
# Powerup coin
# ─────────────────────────────────────────────────────────────────────────────
class Powerup:
    SPEED   = 5.0
    RADIUS  = 18
    BOB_AMP = 6
    BOB_SPD = 0.08

    def __init__(self, ptype, x, name):
        self.ptype     = ptype
        self.x         = float(x)
        self.base_y    = GROUND - 80
        self.bob_t     = random.uniform(0, math.pi*2)
        self.name      = name
        self.collected = False
        self.collect_t = 0

    @property
    def y(self):
        return self.base_y + math.sin(self.bob_t) * self.BOB_AMP

    @property
    def rect(self):
        r = self.RADIUS
        return pygame.Rect(int(self.x)-r, int(self.y)-r, r*2, r*2)

    def update(self, speed_mult=1.0):
        if self.collected:
            self.collect_t += 1
            return
        self.x    -= self.SPEED * speed_mult
        self.bob_t += self.BOB_SPD

    def draw(self, surface, font_small):
        color = POWERUP_TYPES[self.ptype]["color"]
        if self.collected:
            alpha = max(0, 255 - self.collect_t*20)
            if alpha <= 0: return
            s = font_small.render(f"+{self.name}", True, color)
            s.set_alpha(alpha)
            surface.blit(s, (int(self.x)-s.get_width()//2,
                              int(self.y)-30 - self.collect_t*2))
            return
        cx, cy = int(self.x), int(self.y)
        glow = pygame.Surface((self.RADIUS*4, self.RADIUS*4), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*color,40), (self.RADIUS*2, self.RADIUS*2), self.RADIUS*2)
        surface.blit(glow, (cx-self.RADIUS*2, cy-self.RADIUS*2))
        pygame.draw.circle(surface, color, (cx,cy), self.RADIUS)
        pygame.draw.circle(surface, (255,255,255), (cx,cy), self.RADIUS, 2)
        pygame.draw.circle(surface, tuple(min(255,c+80) for c in color),
                           (cx-4,cy-4), self.RADIUS//3)
        lbl = font_small.render(self.name[:7], True, (15,15,15))
        surface.blit(lbl, (cx-lbl.get_width()//2, cy-lbl.get_height()//2))

# ─────────────────────────────────────────────────────────────────────────────
# Score bar
# ─────────────────────────────────────────────────────────────────────────────
class ScoreBar:
    def __init__(self):
        self.values  = {k: 8.0 for k in ["Military","Authority","Prosperity","Descendants"]}
        self.display = dict(self.values)
        self.flash   = {k: 0 for k in self.values}

    def apply_effects(self, effects):
        for key, pct in effects.items():
            if key in self.values:
                self.values[key] = max(0.0, min(20.0, self.values[key]*(1+pct)))
                self.flash[key]  = 45

    def update(self):
        for k in self.values:
            self.display[k] += (self.values[k]-self.display[k])*0.08
            if self.flash[k] > 0: self.flash[k] -= 1

    def any_below(self, t=2.0):
        return any(v < t for v in self.values.values())

    def draw(self, surface, font_small):
        BAR_W, BAR_H = 180, 14
        x0, y0 = W-BAR_W-20, 14
        for i, (name, val) in enumerate(self.values.items()):
            y = y0 + i*36
            color = SCORE_COLORS[name]
            surface.blit(font_small.render(name, True, C_WHITE), (x0, y))
            pygame.draw.rect(surface, (30,30,50), (x0, y+16, BAR_W, BAR_H), border_radius=6)
            fw = int(BAR_W * min(self.display[name],10)/10)
            if fw > 0:
                bc = tuple(min(255,c+60) for c in color) if (self.flash[name]//4)%2==1 else color
                pygame.draw.rect(surface, bc, (x0, y+16, fw, BAR_H), border_radius=6)
            surface.blit(font_small.render(f"{val:.1f}", True, C_GOLD), (x0+BAR_W+5, y+14))

# ─────────────────────────────────────────────────────────────────────────────
# Scrolling background (dynasty-coloured, blends on transition)
# ─────────────────────────────────────────────────────────────────────────────
class Background:
    def __init__(self, dynasty_idx=0):
        self._load(dynasty_idx)
        self.old = None
        self.blend_t = 1.0
        self.stars     = [(random.randint(0,W), random.randint(0,GROUND-80),
                           random.uniform(0.3,1.0)) for _ in range(120)]
        self.mountains = self._gen_mountains()
        self.clouds    = [{"x":random.uniform(0,W),"y":random.uniform(30,120),
                           "w":random.randint(80,180),"s":random.uniform(0.2,0.5)}
                          for _ in range(6)]
        self.scroll = 0.0

    def _load(self, idx):
        d = DYNASTIES[idx]
        self.sky_top  = d["sky_top"]
        self.sky_bot  = d["sky_bot"]
        self.gnd      = d["ground"]
        self.mtn      = d["mountain"]
        self.cld      = d["cloud"]

    def start_transition(self, new_idx):
        self.old = (self.sky_top, self.sky_bot, self.gnd, self.mtn)
        self._load(new_idx)
        self.blend_t = 0.0

    def _gen_mountains(self):
        pts = [(0, GROUND-80)]
        x = 0
        while x < W+200:
            x += random.randint(60,180)
            pts.append((x, random.randint(GROUND-220, GROUND-90)))
        pts.append((W+200, GROUND-80))
        return pts

    def update(self, speed):
        self.scroll += speed*0.3
        for c in self.clouds:
            c["x"] -= c["s"]*speed
            if c["x"] < -200:
                c["x"] = W+100
                c["y"] = random.uniform(30,120)
        if self.blend_t < 1.0:
            self.blend_t = min(1.0, self.blend_t+0.01)

    def _c(self, new, attr_old):
        if self.old is None or self.blend_t >= 1.0:
            return new
        return lerp3(attr_old, new, self.blend_t)

    def draw(self, surface):
        st = self._c(self.sky_top, self.old[0]) if self.old else self.sky_top
        sb = self._c(self.sky_bot, self.old[1]) if self.old else self.sky_bot
        gc = self._c(self.gnd,     self.old[2]) if self.old else self.gnd
        mc = self._c(self.mtn,     self.old[3]) if self.old else self.mtn

        for y in range(GROUND):
            pygame.draw.line(surface, lerp3(st,sb,y/GROUND), (0,y),(W,y))
        for sx,sy,br in self.stars:
            v = int(255*br) if br>0.7 else int(200*br)
            if br > 0.7: pygame.draw.circle(surface,(v,v,v),(sx,sy),1)
            else: surface.set_at((sx,sy),(v,v,v))
        shift = int(self.scroll*0.3) % (W+200)
        for dx in [0, W+200]:
            pts = [(x-shift+dx,y) for x,y in self.mountains]
            closed = pts + [(pts[-1][0],GROUND),(pts[0][0],GROUND)]
            if len(closed) >= 3:
                pygame.draw.polygon(surface, mc, closed)
        for c in self.clouds:
            cs = pygame.Surface((c["w"],30),pygame.SRCALPHA)
            pygame.draw.ellipse(cs, (*self.cld,55),(0,0,c["w"],30))
            surface.blit(cs,(int(c["x"]),int(c["y"])))
        pygame.draw.rect(surface, gc, (0,GROUND,W,H-GROUND))
        pygame.draw.rect(surface, tuple(min(255,c+18) for c in gc),(0,GROUND,W,6))
        for gx in range(int(-self.scroll*0.8)%60-60,W,60):
            pygame.draw.line(surface, tuple(max(0,c-18) for c in gc),
                             (gx,GROUND+8),(gx+20,GROUND+8),1)

# ─────────────────────────────────────────────────────────────────────────────
# Scenario popup
# ─────────────────────────────────────────────────────────────────────────────
class ScenarioPopup:
    PW, PH      = 820, 360
    ANIM_FRAMES = 18

    def __init__(self, challenge_key, obs_images, fonts):
        self.data    = CHALLENGES[challenge_key]
        self.obs_img = obs_images.get(challenge_key)
        self.fonts   = fonts
        self.anim    = 0
        self.closing = False
        self.done    = False
        self._build_buttons()

    def _build_buttons(self):
        opts   = self.data["options"]
        bw,bh  = 320,70
        gap    = 30
        total  = len(opts)*bw+(len(opts)-1)*gap
        sx     = (W-total)//2
        by     = (H-self.PH)//2+self.PH-110
        self.buttons = [{"rect":pygame.Rect(sx+i*(bw+gap),by,bw,bh),
                          "opt":opt,"hover":False} for i,opt in enumerate(opts)]

    def update(self):
        if self.closing:
            self.anim -= 1
            if self.anim <= 0: self.done = True
        else:
            self.anim = min(self.anim+1, self.ANIM_FRAMES)

    def handle_event(self, event):
        if self.closing: return None
        mx,my = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEMOTION:
            for btn in self.buttons: btn["hover"] = btn["rect"].collidepoint(mx,my)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn in self.buttons:
                if btn["rect"].collidepoint(mx,my):
                    self.closing = True
                    return btn["opt"]["effects"]
        return None

    def draw(self, surface):
        t    = self.anim/self.ANIM_FRAMES
        ease = t*t*(3-2*t)
        ov   = pygame.Surface((W,H),pygame.SRCALPHA)
        ov.fill((0,0,0,int(160*ease)))
        surface.blit(ov,(0,0))
        px = (W-self.PW)//2
        py = int((H-self.PH)//2 + self.PH*(1-ease))
        surface.blit(rounded_rect_surf(self.PW,self.PH,18,(18,14,38,245)),(px,py))
        pygame.draw.rect(surface,C_GOLD,(px,py,self.PW,self.PH),3,border_radius=18)
        ts = self.fonts["title"].render(self.data["title"],True,C_GOLD)
        surface.blit(ts,(px+(self.PW-ts.get_width())//2,py+14))
        if self.obs_img:
            surface.blit(pygame.transform.smoothscale(self.obs_img,(90,130)),(px+30,py+60))
        draw_text_wrapped(surface,self.data["scenario"],self.fonts["body"],
                          C_WHITE,pygame.Rect(px+140,py+55,self.PW-170,155))
        pygame.draw.line(surface,C_GOLD,(px+20,py+210),(px+self.PW-20,py+210),1)
        dy = py-(H-self.PH)//2
        for btn in self.buttons:
            r = btn["rect"].copy(); r.y += dy
            bg=(60,42,100) if btn["hover"] else (30,22,55)
            surface.blit(rounded_rect_surf(r.width,r.height,10,(*bg,240)),r.topleft)
            pygame.draw.rect(surface,C_GOLD if btn["hover"] else (100,80,150),r,2,border_radius=10)
            bl = self.fonts["btn"].render(btn["opt"]["text"],True,C_GOLD if btn["hover"] else C_WHITE)
            surface.blit(bl,(r.x+(r.width-bl.get_width())//2,r.y+8))
            parts=[f"{'- ' if v<0 else '+'}{abs(int(v*100))}% {k[:3]}"
                   for k,v in btn["opt"]["effects"].items()]
            el=self.fonts["sub"].render("  ".join(parts),True,(180,140,180))
            surface.blit(el,(r.x+(r.width-el.get_width())//2,r.y+38))

# ─────────────────────────────────────────────────────────────────────────────
# Dynasty intro / transition info screen
# ─────────────────────────────────────────────────────────────────────────────
class DynastyScreen:
    ANIM_IN = 30

    def __init__(self, dynasty_idx, fonts, is_transition=False):
        self.idx   = dynasty_idx
        self.d     = DYNASTIES[dynasty_idx]
        self.fonts = fonts
        self.is_tr = is_transition
        self.anim  = 0
        self.done  = False

    def update(self):
        self.anim = min(self.anim+1, self.ANIM_IN)

    def handle_event(self, event):
        if self.anim < self.ANIM_IN: return
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN):
            self.done = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.done = True

    def draw(self, surface, bg):
        alpha = int(255 * self.anim / self.ANIM_IN)
        ov = pygame.Surface((W,H),pygame.SRCALPHA)
        ov.fill((0,0,0,170))
        ov.set_alpha(alpha)
        surface.blit(ov,(0,0))

        PW, PH = 780, 330
        px, py = (W-PW)//2, (H-PH)//2

        panel = rounded_rect_surf(PW, PH, 20, (15,10,35,230))
        panel.set_alpha(alpha)
        surface.blit(panel,(px,py))
        # gold border
        border = pygame.Surface((PW,PH),pygame.SRCALPHA)
        pygame.draw.rect(border,(*C_GOLD,alpha),(0,0,PW,PH),2,border_radius=20)
        surface.blit(border,(px,py))

        def blita(s, cy):
            sc = s.copy(); sc.set_alpha(alpha)
            surface.blit(sc,(W//2-s.get_width()//2, cy))

        if self.is_tr:
            hdr = self.fonts["small"].render("DYNASTY SURVIVED -- NEXT DYNASTY", True, C_GOLD)
            blita(hdr, py+8)

        blita(self.fonts["huge"].render(self.d["name"],  True, C_GOLD),          py+38)
        blita(self.fonts["title"].render(self.d["years"],True,(180,160,220)),     py+108)

        # blurb
        for i, line in enumerate(self.d["blurb"].split("\n")):
            ls = self.fonts["body"].render(line, True, C_WHITE)
            ls.set_alpha(alpha)
            surface.blit(ls,(W//2-ls.get_width()//2, py+158+i*28))

        # challenge count
        cs = self.fonts["small"].render(
            f"Challenges to survive this dynasty: {self.d['challenges']}", True,(160,210,160))
        blita(cs, py+265)

        # powerup hints
        tech_s = self.fonts["sub"].render(
            f"Tech: {self.d['tech_powerup']}   Talent: {self.d['talent_name']}", True,(160,180,220))
        blita(tech_s, py+290)

        if self.anim >= self.ANIM_IN:
            cont = self.fonts["small"].render("Press SPACE or click to begin", True,(150,130,170))
            blita(cont, py+PH+12)

        badge = self.fonts["small"].render(
            f"Dynasty {self.idx+1} of {len(DYNASTIES)}", True,(140,120,160))
        blita(badge, py-26)

# ─────────────────────────────────────────────────────────────────────────────
# HUD / screen helpers
# ─────────────────────────────────────────────────────────────────────────────
def draw_hud(surface, scores, cleared, dynasty_idx, fonts, paused):
    d = DYNASTIES[dynasty_idx]
    surface.blit(fonts["small"].render(d["name"],True,C_GOLD),(20,14))
    surface.blit(fonts["small"].render(
        f"Challenges: {cleared} / {d['challenges']}",True,C_WHITE),(20,34))
    surface.blit(fonts["small"].render(
        f"Dynasty {dynasty_idx+1} / {len(DYNASTIES)}",True,(160,140,180)),(20,54))
    scores.draw(surface, fonts["small"])
    if paused:
        ps = fonts["title"].render("-- PAUSED --",True,C_GOLD)
        surface.blit(ps,(W//2-ps.get_width()//2,14))


def draw_title(surface, fonts, bg):
    bg.draw(surface)
    ov=pygame.Surface((W,H),pygame.SRCALPHA); ov.fill((0,0,0,120)); surface.blit(ov,(0,0))
    blit_center(surface,fonts["huge"].render("DRAGON RUNNER",True,C_GOLD),110)
    blit_center(surface,fonts["title"].render("A Dynasty Survival Game",True,(200,170,230)),190)
    blit_center(surface,fonts["body"].render(
        "8 dynasties  |  Rising challenge frequency  |  Powerup coins",True,(160,200,160)),255)
    blit_center(surface,fonts["body"].render("Press  SPACE  to begin",True,C_WHITE),318)
    blit_center(surface,fonts["small"].render(
        "Jump over obstacles  |  Keep all 4 scores above 2  |  Collect coins for bonuses",
        True,(150,130,170)),382)


def draw_end(surface, fonts, win, scores, reason=""):
    ov=pygame.Surface((W,H),pygame.SRCALPHA); ov.fill((0,0,0,185)); surface.blit(ov,(0,0))
    if win:
        msg,color = "ALL DYNASTIES ENDURE!", C_GOLD
        sub = "Your dragon guided China through eight great ages."
    else:
        msg,color = "THE DYNASTY FALLS", C_RED
        sub = reason or "The realm crumbles into chaos."
    blit_center(surface,fonts["huge"].render(msg,True,color),100)
    blit_center(surface,fonts["title"].render(sub,True,C_WHITE),178)
    y=240
    for name,val in scores.items():
        blit_center(surface,fonts["body"].render(f"{name}: {val:.1f}",True,SCORE_COLORS[name]),y)
        y+=34
    blit_center(surface,fonts["body"].render("Press  R  to play again",True,(180,160,210)),y+20)

# ─────────────────────────────────────────────────────────────────────────────
# Obstacle spawn interval — randomised, gets shorter each dynasty
# ─────────────────────────────────────────────────────────────────────────────
def obs_interval(dynasty_idx):
    base = max(1.4, 3.5 - dynasty_idx * 0.25)   # 3.5s → ~1.6s at dynasty 8
    return base * random.uniform(0.55, 1.45)     # ±45% randomisation

# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
def make_dragon_frames(base, n=4):
    return [pygame.transform.rotate(base, math.sin(i*math.pi/2)*5) for i in range(n)]


async def main():
    pygame.init()
    screen = pygame.display.set_mode((W,H))
    pygame.display.set_caption("Dragon Runner -- Dynasty Edition")
    clock = pygame.time.Clock()

    def sysf(size, bold=False):
        for name in ["Georgia","Palatino","Times New Roman"]:
            try: return pygame.font.SysFont(name,size,bold=bold)
            except Exception: pass
        return pygame.font.SysFont(None,size,bold=bold)

    fonts = {
        "huge":  sysf(62,True), "title": sysf(34,True),
        "body":  sysf(25),      "btn":   sysf(22,True),
        "small": sysf(17),      "sub":   sysf(15),
    }

    dragon_frames = make_dragon_frames(load_img("dragon.png",(110,80)))
    obs_sizes = {
        "famine":(58,105), "rebellious_general":(68,112), "devious_eunuch":(52,108),
    }
    obs_images = {k: load_img(CHALLENGES[k]["image"],sz) for k,sz in obs_sizes.items()}

    # ── game factory ──────────────────────────────────────────────────────────
    def new_game():
        bg = Background(0)
        return {
            "dragon":         Dragon(dragon_frames),
            "bg":             bg,
            "scores":         ScoreBar(),
            "obstacles":      [],
            "powerups":       [],
            "popup":          None,
            "dynasty_screen": DynastyScreen(0, fonts, is_transition=False),
            "state":          "title",
            # title | dynasty_intro | playing | popup | transition | win | lose
            "dynasty_idx":    0,
            "cleared":        0,
            "speed_mult":     1.0,
            "next_obs_time":  time.time() + obs_interval(0),
            "next_pow_time":  time.time() + random.uniform(4.0, 8.0),
            "talent_spawned": False,
            "lose_reason":    "",
        }

    g = new_game()

    def advance_dynasty():
        nidx = g["dynasty_idx"] + 1
        if nidx >= len(DYNASTIES):
            g["state"] = "win"
            return
        g["dynasty_idx"]    = nidx
        g["cleared"]        = 0
        g["obstacles"]      = []
        g["powerups"]       = []
        g["popup"]          = None
        g["talent_spawned"] = False
        g["speed_mult"]     = 1.0 + nidx*0.10
        g["bg"].start_transition(nidx)
        g["dynasty_screen"] = DynastyScreen(nidx, fonts, is_transition=True)
        g["state"]          = "transition"
        g["next_obs_time"]  = time.time() + 3.0
        g["next_pow_time"]  = time.time() + random.uniform(4.0, 8.0)

    def check_end():
        didx = g["dynasty_idx"]
        if g["scores"].any_below(2.0):
            low = [k for k,v in g["scores"].values.items() if v < 2.0]
            g["lose_reason"] = f"{', '.join(low)} collapsed -- the dynasty falls!"
            g["state"] = "lose"
            return True
        if g["cleared"] >= DYNASTIES[didx]["challenges"]:
            advance_dynasty()
            return True
        return False

    # ── main loop ─────────────────────────────────────────────────────────────
    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                elif event.key == pygame.K_r:
                    g = new_game()
                elif event.key == pygame.K_SPACE:
                    if   g["state"] == "title":       g["state"] = "dynasty_intro"
                    elif g["state"] == "playing":     g["dragon"].jump()
                    elif g["state"] in ("win","lose"): g = new_game()

            if g["state"] in ("dynasty_intro","transition") and g["dynasty_screen"]:
                g["dynasty_screen"].handle_event(event)
            if g["state"] == "popup" and g["popup"]:
                effects = g["popup"].handle_event(event)
                if effects is not None:
                    g["scores"].apply_effects(effects)

        # ── state updates ─────────────────────────────────────────────────────
        if g["state"] in ("dynasty_intro","transition"):
            g["dynasty_screen"].update()
            g["bg"].update(0)
            if g["dynasty_screen"].done:
                g["state"] = "playing"

        elif g["state"] == "playing":
            didx = g["dynasty_idx"]
            g["bg"].update(g["speed_mult"])
            g["dragon"].update()
            now = time.time()

            # spawn obstacle
            if now >= g["next_obs_time"] and not g["obstacles"]:
                key = random.choice(CHALLENGE_KEYS)
                g["obstacles"].append(Obstacle(key, obs_images[key], W+20))
                g["next_obs_time"] = now + obs_interval(didx)

            # spawn powerup (one on screen at a time)
            active_pows = [p for p in g["powerups"] if not p.collected]
            if now >= g["next_pow_time"] and not active_pows:
                # choose type
                if not g["talent_spawned"] and random.random() < 0.30:
                    ptype = "talent"
                    g["talent_spawned"] = True
                else:
                    ptype = random.choice(["tech","harvest","harvest"])
                # name
                d = DYNASTIES[didx]
                pname = (d["tech_powerup"] if ptype=="tech" else
                         d["talent_name"]  if ptype=="talent" else "Harvest")
                g["powerups"].append(Powerup(ptype, W+20, pname))
                g["next_pow_time"] = now + random.uniform(5.0, 11.0)

            for obs in g["obstacles"]:  obs.update(g["speed_mult"])
            for pow_ in g["powerups"]:  pow_.update(g["speed_mult"])

            # obstacle collision → popup
            dhb = g["dragon"].hitbox
            for obs in g["obstacles"]:
                if not obs.triggered and dhb.colliderect(obs.hitbox):
                    obs.triggered       = True
                    g["dragon"].flash_t = 30
                    g["popup"]          = ScenarioPopup(obs.key, obs_images, fonts)
                    g["state"]          = "popup"

            # powerup collection
            dr = g["dragon"].rect
            for pow_ in g["powerups"]:
                if not pow_.collected and dr.colliderect(pow_.rect):
                    pow_.collected = True
                    g["scores"].apply_effects(POWERUP_TYPES[pow_.ptype]["effects"])

            # count cleanly-passed obstacles
            for obs in g["obstacles"]:
                if not obs.triggered and obs.x + obs.image.get_width() < g["dragon"].x-10:
                    g["cleared"] += 1
                    obs.triggered = True

            g["obstacles"] = [o for o in g["obstacles"] if o.x > -200]
            g["powerups"]  = [p for p in g["powerups"]
                              if p.x > -200 or (p.collected and p.collect_t < 18)]
            g["scores"].update()
            g["speed_mult"] = 1.0 + didx*0.10 + g["cleared"]*0.015
            check_end()

        elif g["state"] == "popup" and g["popup"]:
            g["popup"].update()
            g["scores"].update()
            if g["popup"].done:
                g["obstacles"]     = [o for o in g["obstacles"] if not o.triggered]
                g["cleared"]      += 1
                g["popup"]         = None
                g["state"]         = "playing"
                g["next_obs_time"] = time.time() + obs_interval(g["dynasty_idx"]) * 0.8
                check_end()

        # ── draw ─────────────────────────────────────────────────────────────
        if g["state"] == "title":
            draw_title(screen, fonts, g["bg"])

        elif g["state"] in ("dynasty_intro","transition"):
            g["bg"].draw(screen)
            g["dynasty_screen"].draw(screen, g["bg"])

        else:
            g["bg"].draw(screen)
            for pow_ in g["powerups"]:  pow_.draw(screen, fonts["small"])
            for obs in g["obstacles"]:  obs.draw(screen)
            g["dragon"].draw(screen)

            if g["state"] in ("playing","popup"):
                draw_hud(screen, g["scores"], g["cleared"],
                         g["dynasty_idx"], fonts, paused=(g["state"]=="popup"))
            if g["state"] == "popup" and g["popup"]:
                g["popup"].draw(screen)
            if g["state"] == "win":
                draw_end(screen, fonts, win=True, scores=g["scores"].values)
            elif g["state"] == "lose":
                draw_end(screen, fonts, win=False, scores=g["scores"].values,
                         reason=g["lose_reason"])

        pygame.display.flip()

        await asyncio.sleep(0)


if __name__ == "__main__":
    asyncio.run(main()) # <--- UPDATE THIS LINE