import fs from "node:fs";
import path from "node:path";

const LIB = "${process.env.HOME}/.codex/skills/claude-animation/lib";
const {
  clamp, lerp, rad, ss, eOut, eIO, eBack, popS,
  at, line, poly, smooth, ellipse, stroke, fill, hatch, burst, INK
} = await import(path.join(LIB, "core.mjs"));
const { Pen } = await import(path.join(LIB, "pen.mjs"));
const { paper, lightBands, sun, grass, soil, filmFinish } = await import(path.join(LIB, "textures.mjs"));
const { sprout, blossom, bee } = await import(path.join(LIB, "nature.mjs"));
const { ant, antGuides } = await import(path.join(LIB, "rigs/ant.mjs"));
const { leaf, leafPiece, egg, larva, cocoon, fungus, roots, nestCanvas } = await import(path.join(LIB, "colony.mjs"));
const { run, exposure } = await import(path.join(LIB, "film.mjs"));

const timeline = JSON.parse(fs.readFileSync("work/handdrawn_audio/timeline.json", "utf-8"));

const W = 1920, H = 1080, FPS = 25, DUR = 21.0;
const C_RED = "#C84324";
const C_BLUE = "#3D6CB9";
const C_GREEN = "#4F8E39";
const C_GOLD = "#D99126";
const C_PAPER = "#F5EFE0";
const C_SUB_BG = "rgba(246, 240, 226, 0.92)";

// Helper: hand-drawn callout card with Pen watercolor wash + overshooting pencil box
function drawCalloutCard(ctx, pen, id, x, y, w, h, reveal, bgWash, borderCol, title, sub) {
  if (reveal <= 0) return;
  const r = clamp(reveal);
  ctx.save();
  const s = 0.88 + 0.12 * eBack(r);
  ctx.translate(x + w / 2, y + h / 2);
  ctx.scale(s, s);
  ctx.translate(-w / 2, -h / 2);

  // Soft paper base so text is 100% legible over soil/grass
  ctx.fillStyle = "rgba(248, 243, 232, 0.94)";
  ctx.beginPath();
  ctx.roundRect(0, 0, w, h, 14);
  ctx.fill();

  pen.begin(id, r);
  pen.wash([[6, 6], [w - 6, 6], [w - 6, h - 6], [6, h - 6]], bgWash, { alpha: 0.32, solid: false });
  pen.box(0, 0, w, h, { w: 3.5, color: borderCol, over: 10 });
  pen.end();

  ctx.globalAlpha = clamp(r * 1.4);
  ctx.fillStyle = borderCol;
  ctx.font = 'bold 30px "PingFang SC", "Hiragino Sans GB", sans-serif';
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(title, w / 2, sub ? h * 0.38 : h * 0.5);

  if (sub) {
    ctx.fillStyle = "#3E3024";
    ctx.font = '600 20px "PingFang SC", "Hiragino Sans GB", sans-serif';
    ctx.fillText(sub, w / 2, h * 0.72);
  }
  ctx.restore();
}

// Helper: draw word-synchronized bilingual captions at bottom
function drawCaptions(ctx, t) {
  const activeLine = timeline.lines.find(l => t >= l.start - 0.12 && t <= l.end + 0.22);
  if (!activeLine) return;

  const fade = clamp((t - (activeLine.start - 0.12)) / 0.15) * clamp(((activeLine.end + 0.22) - t) / 0.18);
  ctx.save();
  ctx.globalAlpha = fade;

  // Measure full Chinese line width using word tokens
  ctx.font = 'bold 34px "PingFang SC", "Hiragino Sans GB", sans-serif';
  const tokens = activeLine.words;
  // Also attach punctuation from activeLine.zh so punctuation displays naturally
  const zhFull = activeLine.zh;
  // Map each token to its slice in zhFull
  const segments = [];
  let pos = 0;
  for (let i = 0; i < tokens.length; i++) {
    const tk = tokens[i];
    const idx = zhFull.indexOf(tk.text, pos);
    if (idx > pos) {
      segments.push({ text: zhFull.slice(pos, idx), word: null });
    }
    segments.push({ text: tk.text, word: tk });
    pos = (idx >= 0 ? idx : pos) + tk.text.length;
  }
  if (pos < zhFull.length) {
    segments.push({ text: zhFull.slice(pos), word: null });
  }

  const widths = segments.map(s => ctx.measureText(s.text).width);
  const totalW = widths.reduce((a, b) => a + b, 0);
  const boxW = Math.max(920, totalW + 96);
  const boxH = 108;
  const boxX = (W - boxW) / 2;
  const boxY = H - 134;

  // Storybook parchment bar
  ctx.fillStyle = C_SUB_BG;
  ctx.strokeStyle = "#3B2B1E";
  ctx.lineWidth = 2.8;
  ctx.beginPath();
  ctx.roundRect(boxX, boxY, boxW, boxH, 16);
  ctx.fill();
  ctx.stroke();

  // Inner subtle rule
  ctx.strokeStyle = "rgba(90, 65, 42, 0.22)";
  ctx.lineWidth = 1.2;
  ctx.beginPath();
  ctx.roundRect(boxX + 6, boxY + 6, boxW - 12, boxH - 12, 12);
  ctx.stroke();

  // Draw Chinese words with active karaoke highlight
  let curX = (W - totalW) / 2;
  const zhY = boxY + 42;
  ctx.textAlign = "left";
  ctx.textBaseline = "middle";

  for (let i = 0; i < segments.length; i++) {
    const seg = segments[i];
    const w = widths[i];
    const tk = seg.word;
    const isNow = tk && t >= tk.start - 0.02 && t <= tk.end + 0.06;
    const isPast = tk && t > tk.end + 0.06;

    if (isNow) {
      // Warm highlight pill behind active spoken word
      ctx.fillStyle = "rgba(200, 67, 36, 0.16)";
      ctx.beginPath();
      ctx.roundRect(curX - 4, zhY - 22, w + 8, 42, 8);
      ctx.fill();

      // Active underline
      ctx.strokeStyle = C_RED;
      ctx.lineWidth = 3.5;
      ctx.beginPath();
      ctx.moveTo(curX, zhY + 20);
      ctx.lineTo(curX + w, zhY + 20);
      ctx.stroke();
    }

    ctx.font = 'bold 34px "PingFang SC", "Hiragino Sans GB", sans-serif';
    ctx.fillStyle = isNow ? C_RED : (isPast ? "#1E140C" : "#5A4A3B");
    const lift = isNow ? -3 : 0;
    ctx.fillText(seg.text, curX, zhY + lift);
    curX += w;
  }

  // English subtitle below
  ctx.font = 'italic 21px "Georgia", "Times New Roman", serif';
  ctx.fillStyle = "#5C4938";
  ctx.textAlign = "center";
  ctx.fillText(activeLine.en, W / 2, boxY + 82);

  ctx.restore();
}

// Top-left Storybook Header Stamp
function drawStoryHeader(ctx, pen, chapterText) {
  ctx.save();
  ctx.font = 'bold 21px "PingFang SC", "Hiragino Sans GB", sans-serif';
  const tw = ctx.measureText(chapterText).width;
  ctx.fillStyle = "rgba(246, 240, 226, 0.92)";
  ctx.strokeStyle = "#3B2B1E";
  ctx.lineWidth = 2.4;
  ctx.beginPath();
  ctx.roundRect(42, 34, tw + 74, 52, 12);
  ctx.fill();
  ctx.stroke();

  ctx.fillStyle = C_RED;
  ctx.beginPath();
  ctx.arc(68, 60, 8, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = "#2B1E14";
  ctx.font = 'bold 21px "PingFang SC", "Hiragino Sans GB", sans-serif';
  ctx.textAlign = "left";
  ctx.textBaseline = "middle";
  ctx.fillText(chapterText, 88, 60);
  ctx.restore();
}

run({
  name: "leafcutter-story",
  W, H, fps: FPS, dur: DUR, sheetScale: 0.42,
  out: path.join(process.cwd(), "work/handdrawn_out"),

  setup(ctx) {
    // Pre-bake static paper, meadow soil, and deep underground nest cross-section
    const bgPaper = paper(W, H, "#F4EFE1");
    const surfaceSoil = soil(W, 420, "day");
    const nest = nestCanvas({
      W,
      H: 1300,
      ground: 260,
      seed: 19,
      chambers: [
        { id: "fungus", x: 960, y: 720, rx: 330, ry: 175 },
        { id: "nursery", x: 420, y: 840, rx: 210, ry: 125 },
        { id: "royal", x: 1510, y: 830, rx: 220, ry: 130 }
      ],
      tunnels: [
        [[640, 260], [690, 430], [790, 560], [880, 640]],
        [[1280, 260], [1230, 440], [1120, 560], [1040, 640]],
        [[650, 740], [560, 790], [490, 820]],
        [[1270, 740], [1360, 785], [1430, 815]]
      ]
    });
    const finish = filmFinish(W, H, { grain: 0.08, vig: 0.18 });
    const pen = new Pen(ctx);
    // Warm up Pen weights at reveal=1 so partial reveals know total stroke weights
    return { bgPaper, surfaceSoil, nest, finish, pen };
  },

  frame(ctx, t, i, S) {
    // Step character poses on twos (12.5 fps hand-drawn cadence), keep camera & captions on ones (25 fps)
    const d = exposure(t, [{ at: 0, on: 2 }], FPS);
    const { pen } = S;

    ctx.drawImage(S.bgPaper, 0, 0);

    // ========================================================================
    // SCENE 1 (0.00s - 5.20s): SURFACE MEADOW — SKETCH BUILD-UP & 10x LEAF CARRY
    // ========================================================================
    if (t < 5.20) {
      const G = 720;
      lightBands(ctx, W, H, t);
      sun(ctx, 1650, 150, 95);

      // Distant hand-drawn hills washed in sage watercolor
      pen.begin("s1/hills", 1);
      pen.wash([[0, G], [360, G - 130], [880, G - 75], [1440, G - 145], [W, G - 60], [W, G]], "#C9DFB8", { alpha: 0.45 });
      pen.end();

      ctx.drawImage(S.surfaceSoil, 0, G);
      line(ctx, [[0, G], [W, G]], 3.5);
      grass(ctx, G, 0, W, 24, 14);

      // Meadow plants
      at(ctx, 280, G, 1.25, 0, () => sprout(ctx, { sway: Math.sin(d * 2.5) * 0.6 }));
      at(ctx, 1560, G, 1.35, 0, () => sprout(ctx, { sway: Math.cos(d * 2.2) * 0.6 }));
      at(ctx, 430, G - 75, 0.95, 0, () => blossom(ctx));
      at(ctx, 1440, G - 82, 0.9, 0, () => blossom(ctx));

      // Freshly cut big leaf on the right shrub
      const cutRad = lerp(0, 78, ss(1.4, 2.0, t));
      at(ctx, 1340, G - 165, 0.65, rad(-14), () => leaf(ctx, 540, { cut: cutRad > 2 ? [-90, -55, cutRad] : null }));

      // Hero leafcutter ant:
      // 0.0 -> 0.55s: blue construction guides sketch in
      // 0.45 -> 1.15s: ink -> fill -> texture layers build up
      // 1.20 -> 4.90s: walks left carrying giant 10x leaf overhead
      const guideA = clamp(1 - ss(0.85, 1.35, t));
      const inkA = ss(0.30, 0.70, t);
      const fillA = ss(0.55, 0.95, t);
      const texA = ss(0.80, 1.20, t);

      const walkProg = eIO(ss(1.35, 4.75, d));
      const antX = lerp(1190, 680, walkProg);
      const isWalking = t > 1.35 && t < 4.75;
      const liftP = popS(d, 1.75, 0.38);

      if (guideA > 0.01) {
        ctx.save();
        ctx.globalAlpha = guideA;
        antGuides(ctx, antX, G, 1.35, ss(0.0, 0.50, t), { flip: true, w: 2.2 });
        ctx.restore();
      }

      ant(ctx, antX, G, 1.35, {
        flip: true,
        gait: isWalking ? d * 10.5 : undefined,
        ant: Math.sin(d * 6) * 0.45,
        jaw: isWalking ? 0.35 : 0.15,
        dust: isWalking ? 0.65 : 0,
        look: { ink: inkA, fill: fillA, tex: texA },
        overhead: liftP > 0.02 ? (c) => {
          at(c, -20, -25, 1.85 * liftP, rad(-10 + Math.sin(d * 5) * 3), () => leafPiece(c, 88));
        } : undefined
      });

      // Word-aligned Event 1: "十倍" @ 2.760s -> Callout card "10× 自身体重"
      if (t >= 2.76) {
        const r1 = clamp((t - 2.76) / 0.35);
        drawCalloutCard(
          ctx, pen, "card/10x",
          160, 150, 390, 118, r1,
          "#9FD47C", C_GREEN,
          "叶片重量 ≈ 10× 体重",
          "相当于人类单手举起一辆小轿车"
        );
        pen.begin("card/10x-arrow", r1);
        pen.stroke([[555, 225], [antX - 135, G - 340]], { w: 3.5, color: C_GREEN });
        pen.end();
      }

      // Word-aligned Event 2: "不吃一口" @ 4.367s -> Red stamp card "✗ 绝不直接食用"
      if (t >= 4.367) {
        const r2 = clamp((t - 4.367) / 0.30);
        drawCalloutCard(
          ctx, pen, "card/noeat",
          1120, 150, 390, 118, r2,
          "#F4A698", C_RED,
          "✗ 从不直接吃树叶",
          "成虫无法消化坚硬的叶片纤维"
        );
        pen.begin("card/noeat-arrow", r2);
        pen.stroke([[1115, 225], [antX + 60, G - 310]], { w: 3.5, color: C_RED });
        pen.end();
      }

      drawStoryHeader(ctx, pen, "第一章 · 举叶远征（Sketch → Ink → Watercolour）");
    }

    // ========================================================================
    // SCENE 2 (5.20s - 9.95s): CAMERA DIVES UNDERGROUND -> FUNGUS CULTIVATION
    // ========================================================================
    else if (t < 9.95) {
      const lt = t - 5.20;
      // Camera pans down from surface (camY = 0) into underground nest (camY = 250)
      const camY = lerp(0, 240, eIO(clamp(lt / 1.45)));

      ctx.save();
      ctx.translate(0, -camY);

      // Sky & surface above ground=260
      sun(ctx, 1680, 95, 70);
      ctx.drawImage(S.nest.canvas, 0, 0);
      grass(ctx, 260, 0, W, 18, 12);
      roots(ctx, 250, 265, 240, 3, 6);
      roots(ctx, 1660, 265, 260, 8, 6);

      // Ants marching down left & right tunnels carrying cut leaf fragments
      const pathL = S.nest.paths[0];
      const pathR = S.nest.paths[1];
      for (let k = 0; k < 2; k++) {
        const uL = ((lt * 0.28 + k * 0.45) % 1);
        const pL = pathL.at(uL * pathL.length);
        at(ctx, pL.x, pL.y, 1, pL.angle, () => {
          ant(ctx, 0, 0, 0.52, {
            gait: d * 12 + k,
            overhead: (c) => at(c, 0, -10, 0.9, 0, () => leafPiece(c, 62))
          });
        });

        const uR = ((lt * 0.25 + k * 0.48 + 0.2) % 1);
        const pR = pathR.at(uR * pathR.length);
        at(ctx, pR.x, pR.y, 1, pR.angle + Math.PI, () => {
          ant(ctx, 0, 0, 0.52, {
            flip: true,
            gait: d * 12 + k,
            overhead: (c) => at(c, 0, -10, 0.85, 0, () => leafPiece(c, 58))
          });
        });
      }

      // Central chamber (x=960, y=720): mulch pile + blooming white symbiotic fungus
      const fungusGrow = clamp(0.25 + 0.75 * ss(1.8, 4.2, lt));
      // Green leaf mulch layer at bottom of fungus garden
      for (let m = -4; m <= 4; m++) {
        at(ctx, 960 + m * 55, 815 + (m % 2) * 8, 0.42, m * 0.3, () => leafPiece(ctx, 50));
      }
      at(ctx, 960, 805, 1.22, 0, () => fungus(ctx, 410, 195, fungusGrow, 11));

      // Two gardener ants tending the fungus
      ant(ctx, 745, 825, 0.62, { gait: undefined, headDip: Math.sin(d * 6) * 10, ant: Math.sin(d * 7) * 0.5 });
      ant(ctx, 1175, 825, 0.62, { flip: true, gait: undefined, headDip: Math.cos(d * 6) * 10, ant: Math.cos(d * 7) * 0.5 });

      // Side chambers preview (brood & queen)
      at(ctx, 420, 895, 1.1, 0, () => {
        egg(ctx, 1.2);
        at(ctx, -55, -5, 1.2, 0, () => larva(ctx, 1, Math.sin(d * 4)));
        at(ctx, 55, -8, 1.2, 0, () => cocoon(ctx, 1));
      });
      ant(ctx, 1510, 895, 0.78, { flip: true, gaster: 1.65, ant: Math.sin(d * 4) * 0.3 });

      // Word-aligned Event 3: "碎叶" @ 6.996s -> Label on leaf mulch
      if (t >= 6.996) {
        const rMulch = clamp((t - 6.996) / 0.32);
        drawCalloutCard(
          ctx, pen, "card/mulch",
          260, 520, 360, 110, rMulch,
          "#A9D886", C_GREEN,
          "① 嚼碎叶片铺成培养床",
          "碎叶提供潮湿有机底物"
        );
        pen.begin("card/mulch-line", rMulch);
        pen.stroke([[620, 585], [820, 775]], { w: 3.2, color: C_GREEN });
        pen.end();
      }

      // Word-aligned Event 4: "共生真菌" @ 8.893s -> Callout card on white fungus garden
      if (t >= 8.893) {
        const rFungus = clamp((t - 8.893) / 0.32);
        drawCalloutCard(
          ctx, pen, "card/fungus",
          1290, 510, 390, 116, rFungus,
          "#9EC3F2", C_BLUE,
          "② 培育白色共生真菌",
          "白环蘑属真菌（Leucoagaricus）"
        );
        pen.begin("card/fungus-line", rFungus);
        pen.stroke([[1290, 575], [1110, 690]], { w: 3.2, color: C_BLUE });
        pen.end();
      }

      ctx.restore();
      drawStoryHeader(ctx, pen, "第二章 · 深入地下蚁穴剖面（地下真菌农场）");
    }

    // ========================================================================
    // SCENE 3 (9.95s - 15.25s): MICROSCOPIC CELLULOSE -> GONGYLIDIA -> COLONY FEEDING
    // ========================================================================
    else if (t < 15.25) {
      const lt = t - 9.95;

      // Left half: Hand-drawn Microscopic Conversion Diagram on warm paper
      // Right half: Underground Nursery & Queen being fed golden nutrient bulbs
      pen.begin("s3/panel-left", 1);
      pen.wash([[80, 125], [920, 125], [920, 885], [80, 885]], "#E8DEC8", { alpha: 0.45 });
      pen.box(80, 125, 840, 760, { w: 3.5, color: "#3B2B1E", over: 12 });
      pen.end();

      pen.begin("s3/panel-right", 1);
      pen.wash([[980, 125], [1840, 125], [1840, 885], [980, 885]], "#DFC7A7", { alpha: 0.55 });
      pen.box(980, 125, 860, 760, { w: 3.5, color: "#3B2B1E", over: 12 });
      pen.end();

      // Panel Titles
      ctx.fillStyle = "#2B1E14";
      ctx.font = 'bold 28px "PingFang SC", "Hiragino Sans GB", sans-serif';
      ctx.textAlign = "center";
      ctx.fillText("【微观生化机制：真菌替蚂蚁消化纤维】", 500, 178);
      ctx.fillText("【育幼室与王室：菌丝球哺育全群】", 1410, 178);

      // Step 1 inside Left Panel: Leaf Cellulose ("纤维素" @ 11.190s)
      const cellP = clamp((t - 10.15) / 0.65);
      at(ctx, 290, 340, 0.95 * eBack(cellP), rad(-8), () => leafPiece(ctx, 82));

      if (t >= 11.19) {
        const rCell = clamp((t - 11.19) / 0.35);
        drawCalloutCard(
          ctx, pen, "card/cellulose",
          430, 265, 420, 125, rCell,
          "#A9D886", C_GREEN,
          "植物纤维素（Cellulose）",
          "真菌分泌酶将其分解为可吸收糖分"
        );
      }

      // Hand-drawn downward conversion arrow
      const arrP = clamp((t - 11.8) / 0.5);
      if (arrP > 0) {
        pen.begin("s3/arrow-down", arrP);
        pen.stroke([[500, 425], [500, 535]], { w: 5, color: C_RED });
        pen.stroke([[478, 508], [500, 538], [522, 508]], { w: 5, color: C_RED });
        pen.end();
      }

      // Step 2 inside Left Panel: Gongylidia nutrient bulbs ("菌丝球" @ 13.076s)
      const bulbP = clamp((t - 12.3) / 0.6);
      if (bulbP > 0) {
        at(ctx, 290, 710, 0.9 * bulbP, 0, () => fungus(ctx, 210, 120, 1, 5));
        // Golden swollen hyphal tips (gongylidia)
        const tips = [[-55, -85], [-15, -110], [32, -95], [68, -68], [5, -62]];
        tips.forEach(([tx, ty], idx) => {
          const r = 16 * popS(t, 12.5 + idx * 0.1, 0.35);
          if (r > 0.5) {
            ctx.save();
            ctx.translate(290 + tx, 710 + ty);
            ellipse(ctx, 0, 0, r, r * 1.15);
            fill(ctx, C_GOLD);
            stroke(ctx, 2.4, INK);
            ellipse(ctx, -r * 0.3, -r * 0.3, r * 0.28, r * 0.35);
            fill(ctx, "#FFF7D6");
            ctx.restore();
          }
        });
      }

      if (t >= 13.076) {
        const rBulb = clamp((t - 13.076) / 0.35);
        drawCalloutCard(
          ctx, pen, "card/gongylidia",
          430, 585, 420, 130, rBulb,
          "#F7D88B", C_GOLD,
          "富含营养的「菌丝球」",
          "富含糖类、氨基酸与脂质（唯一主食）"
        );
      }

      // Right Panel: Nursery Chamber (Top) & Queen Chamber (Bottom)
      // Draw warm chamber ovals
      ctx.save();
      ellipse(ctx, 1410, 385, 360, 135);
      fill(ctx, "#EED2A9");
      stroke(ctx, 3.2, "#3B2B1E");

      ellipse(ctx, 1410, 695, 360, 145);
      fill(ctx, "#EED2A9");
      stroke(ctx, 3.2, "#3B2B1E");
      ctx.restore();

      // Top chamber: nurse ant feeding larvae & eggs with a golden gongylidium bulb
      ant(ctx, 1245, 445, 0.72, {
        gait: undefined,
        ant: Math.sin(d * 6) * 0.4,
        carry: (c) => {
          ellipse(c, 0, 0, 15, 15);
          fill(c, C_GOLD);
          stroke(c, 2, INK);
        }
      });
      at(ctx, 1435, 430, 1.45, 0, () => larva(ctx, 1, Math.sin(d * 5)));
      at(ctx, 1535, 432, 1.4, 0, () => larva(ctx, 1, Math.cos(d * 5)));
      at(ctx, 1625, 438, 1.35, 0, () => cocoon(ctx, 1));
      at(ctx, 1690, 445, 1.35, 0, () => egg(ctx, 1));

      // Bottom chamber: Queen ant & worker ("整座蚁群" @ 14.270s)
      ant(ctx, 1530, 775, 0.92, {
        flip: true,
        gaster: 1.7,
        ant: Math.sin(d * 4) * 0.35
      });
      ant(ctx, 1235, 775, 0.66, {
        gait: undefined,
        headDip: Math.sin(d * 5) * 8,
        carry: (c) => {
          ellipse(c, 0, 0, 14, 14);
          fill(c, C_GOLD);
          stroke(c, 2, INK);
        }
      });

      if (t >= 14.27) {
        const rColony = clamp((t - 14.27) / 0.32);
        drawCalloutCard(
          ctx, pen, "card/colony",
          1170, 505, 480, 96, rColony,
          "#F4A698", C_RED,
          "哺育整座百万级蚁群（幼虫 · 工蚁 · 蚁后）",
          ""
        );
      }

      drawStoryHeader(ctx, pen, "第三章 · 纤维素转化与菌丝球哺育（共生闭环）");
    }

    // ========================================================================
    // SCENE 4 (15.25s - 21.00s): 50 MILLION YEARS OF EVOLUTIONARY AGRICULTURE
    // ========================================================================
    else {
      const lt = t - 15.25;
      const G = 675;

      lightBands(ctx, W, H, t);
      sun(ctx, 1690, 140, 88);
      ctx.drawImage(S.surfaceSoil, 0, G);
      line(ctx, [[0, G], [W, G]], 3.5);
      grass(ctx, G, 0, W, 22, 13);

      // Caravan of 3 leafcutter ants marching across the meadow
      for (let k = 0; k < 3; k++) {
        const ax = lerp(1650, 280, clamp((lt * 0.16 + k * 0.24) % 1));
        ant(ctx, ax, G, 0.88, {
          flip: true,
          gait: d * 10 + k * 2,
          ant: Math.sin(d * 6 + k) * 0.4,
          overhead: (c) => at(c, -15, -20, 1.45, rad(-8 + Math.sin(d * 4 + k) * 4), () => leafPiece(c, 74))
        });
      }

      // Bee drifting in the sky
      at(ctx, lerp(1480, 420, clamp(lt / 5.2)), 195 + Math.sin(d * 12) * 8, 1.0, 0, () => bee(ctx, t));

      // Underground fungus chamber vignette at bottom
      ctx.save();
      ellipse(ctx, 960, 815, 360, 110);
      fill(ctx, "#2A180C");
      ellipse(ctx, 960, 815, 350, 102);
      fill(ctx, "#E8C696");
      stroke(ctx, 3.2, "#2A180C");
      at(ctx, 960, 885, 0.95, 0, () => fungus(ctx, 360, 140, 1, 11));
      ctx.restore();

      // Evolutionary Timeline Scroll across the upper sky
      const scrollP = clamp(lt / 0.65);
      pen.begin("s4/scroll", scrollP);
      pen.wash([[160, 110], [1760, 110], [1760, 415], [160, 415]], "#EFE5CE", { alpha: 0.88, over: true });
      pen.box(160, 110, 1600, 305, { w: 4, color: "#3B2B1E", over: 14 });
      pen.stroke([[260, 262], [1660, 262]], { w: 5, color: "#3B2B1E" });
      pen.end();

      // Word-aligned Event 5: "五千万年前" @ 16.722s -> Left milestone (-50,000,000 years)
      if (t >= 16.722) {
        const r50m = clamp((t - 16.722) / 0.38);
        drawCalloutCard(
          ctx, pen, "card/50m",
          240, 130, 580, 115, r50m,
          "#9FD47C", C_GREEN,
          "50,000,000 年前 · 切叶蚁演化出真菌农业",
          "集采集、控温控湿、除杂菌于一体的生态工程"
        );
        drawCalloutCard(
          ctx, pen, "card/human",
          1100, 130, 560, 115, r50m,
          "#DFC7A7", "#6E553E",
          "仅 10,000 年前 · 人类才学会农业耕种",
          "切叶蚁比人类早了整整五千万年"
        );
      }

      // Word-aligned Event 6: "地下农业" @ 19.033s -> Final Storybook Seal Stamp
      if (t >= 19.033) {
        const rAgri = clamp((t - 19.033) / 0.35);
        drawCalloutCard(
          ctx, pen, "card/agri-seal",
          560, 282, 800, 112, rAgri,
          "#F4A698", C_RED,
          "切叶蚁的地下农业帝国 · 纯代码手绘科普",
          "Pen 笔刷水彩 + 骨骼动画 + 词级对齐字幕 · 零生图大模型"
        );
      }

      drawStoryHeader(ctx, pen, "第四章 · 五千万年的地下农业演化史");
    }

    // Draw word-synchronized bilingual captions on top
    drawCaptions(ctx, t);

    // Paper grain + subtle vignette finish
    S.finish(ctx, i);
  }
});
