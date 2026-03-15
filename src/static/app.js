const DEFAULT_EVENT_RATE = 280;
const PANEL_ORDER = ["BFS", "DFS", "Dijkstra", "A*"];
const COLORS = {
  wall: "#0f1b30",
  passage: "#fbf7ef",
  passageShadow: "rgba(17, 32, 56, 0.16)",
  visited: "#f59a23",
  path: "#8cf529",
  start: "#0ca678",
  goal: "#db4c30",
  text: "#15253f",
};

const dom = {
  form: document.querySelector("#controls"),
  size: document.querySelector("#size"),
  seed: document.querySelector("#seed"),
  weighted: document.querySelector("#weighted"),
  loopFactor: document.querySelector("#loop-factor"),
  loopFactorValue: document.querySelector("#loop-factor-value"),
  speed: document.querySelector("#speed"),
  speedValue: document.querySelector("#speed-value"),
  seedDisplay: document.querySelector("#seed-display"),
  modeDisplay: document.querySelector("#mode-display"),
  mazeDisplay: document.querySelector("#maze-display"),
  runStatus: document.querySelector("#run-status"),
  tableBody: document.querySelector("#comparison-table tbody"),
  panelGrid: document.querySelector("#panel-grid"),
  panels: [...document.querySelectorAll(".solver-panel")],
  runButton: document.querySelector("#run-button"),
};

const state = {
  payload: null,
  panelStates: new Map(),
  animationFrame: null,
  lastTick: 0,
  speedMultiplier: Number(dom.speed.value),
  eventRate: DEFAULT_EVENT_RATE,
};

dom.speed.addEventListener("input", () => {
  state.speedMultiplier = Number(dom.speed.value);
  dom.speedValue.textContent = `${state.speedMultiplier.toFixed(2)}x`;
});

dom.loopFactor.addEventListener("input", () => {
  dom.loopFactorValue.textContent = Number(dom.loopFactor.value).toFixed(2);
});

dom.form.addEventListener("submit", async (event) => {
  event.preventDefault();
  await loadRun(true);
});

window.addEventListener("resize", () => renderAll(performance.now()));

async function loadRun(focusPanels = false) {
  cancelAnimationFrame(state.animationFrame);
  setRunState("Generating maze and running Python solvers...");
  dom.runButton.disabled = true;
  dom.runButton.textContent = "Running...";

  const body = {
    size: Number(dom.size.value),
    weighted: dom.weighted.checked,
    loop_factor: Number(dom.loopFactor.value),
  };
  if (dom.seed.value.trim() !== "") {
    body.seed = Number(dom.seed.value);
  }

  try {
    const response = await fetch("/api/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }
    const payload = await response.json();
    prepareRun(payload, focusPanels);
  } catch (error) {
    setRunState(error.message);
  } finally {
    dom.runButton.disabled = false;
    dom.runButton.textContent = "Generate and Run";
  }
}

function prepareRun(payload, focusPanels = false) {
  state.payload = payload;
  state.eventRate = deriveEventRate(payload.algorithms);
  dom.seed.value = payload.seed;
  dom.seedDisplay.textContent = payload.seed;
  dom.modeDisplay.textContent = payload.maze.weighted ? "Weighted" : "Unweighted";
  dom.mazeDisplay.textContent = `${payload.maze.logical_size} x ${payload.maze.logical_size}`;
  dom.loopFactor.value = payload.maze.loop_factor.toFixed(2);
  dom.loopFactorValue.textContent = payload.maze.loop_factor.toFixed(2);

  buildComparisonTable(payload.algorithms);
  initializePanels(payload);
  setRunState("Animating solver traces...");
  if (focusPanels) {
    dom.panelGrid.scrollIntoView({ behavior: "smooth", block: "start" });
  }
  state.lastTick = performance.now();
  state.animationFrame = requestAnimationFrame(animationLoop);
}

function buildComparisonTable(results) {
  dom.tableBody.innerHTML = "";

  for (const result of PANEL_ORDER.map((name) =>
    results.find((item) => item.algorithm === name)
  )) {
    const row = document.createElement("tr");
    row.dataset.algorithm = result.algorithm;
    row.innerHTML = `
      <td><strong>${result.algorithm}</strong></td>
      <td>${result.metrics.nodes_explored}</td>
      <td>${result.metrics.runtime_ms.toFixed(3)} ms</td>
      <td>${result.metrics.path_length}</td>
      <td>${result.metrics.path_cost}</td>
      <td>${result.status.found ? "Yes" : "No"}</td>
    `;
    dom.tableBody.append(row);
  }
}

function initializePanels(payload) {
  state.panelStates.clear();

  for (const panel of dom.panels) {
    const algorithm = panel.dataset.algorithm;
    const result = payload.algorithms.find((item) => item.algorithm === algorithm);
    const canvas = panel.querySelector("canvas");
    const context = canvas.getContext("2d");
    const dynamicGrid = payload.maze.grid.map((row) =>
      row.map(() => ({
        visitedAt: null,
        pathAt: null,
      }))
    );

    state.panelStates.set(algorithm, {
      algorithm,
      panel,
      canvas,
      context,
      result,
      dynamicGrid,
      eventIndex: 0,
      eventBudget: 0,
      complete: false,
      pathCount: 0,
    });

    panel.querySelector(".panel-state").textContent = "Queued";
  }
}

function animationLoop(now) {
  const delta = now - state.lastTick;
  state.lastTick = now;
  let allComplete = true;

  for (const panelState of state.panelStates.values()) {
    if (!panelState.complete) {
      allComplete = false;
      panelState.eventBudget += (delta / 1000) * state.eventRate * state.speedMultiplier;
      while (panelState.eventBudget >= 1 && panelState.eventIndex < panelState.result.events.length) {
        panelState.eventBudget -= 1;
        applyEvent(panelState, panelState.result.events[panelState.eventIndex], now);
        panelState.eventIndex += 1;
      }

      if (panelState.eventIndex >= panelState.result.events.length) {
        panelState.complete = true;
        panelState.panel.querySelector(".panel-state").textContent = "Complete";
        const row = dom.tableBody.querySelector(`[data-algorithm="${panelState.algorithm}"]`);
        if (row) {
          row.classList.add("is-complete");
        }
      }
    }

    renderPanel(panelState, now);
  }

  if (allComplete) {
    setRunState("All traces complete.");
    renderAll(now);
    return;
  }

  state.animationFrame = requestAnimationFrame(animationLoop);
}

function applyEvent(panelState, event, now) {
  const cell = panelState.dynamicGrid[event.row][event.col];
  if (event.kind === "discover") {
    panelState.panel.querySelector(".panel-state").textContent = "Searching";
    return;
  }

  if (event.kind === "expand") {
    cell.visitedAt = now;
    panelState.panel.querySelector(".panel-state").textContent = "Exploring";
    return;
  }

  if (event.kind === "path") {
    cell.visitedAt = null;
    cell.pathAt = now + panelState.pathCount * 24;
    panelState.pathCount += 1;
    panelState.panel.querySelector(".panel-state").textContent = "Revealing path";
  }
}

function renderAll(now) {
  for (const panelState of state.panelStates.values()) {
    renderPanel(panelState, now);
  }
}

function renderPanel(panelState, now) {
  if (!state.payload) {
    return;
  }

  const maze = state.payload.maze;
  const displaySize = resizeCanvas(panelState.canvas, panelState.context);
  const ctx = panelState.context;
  const width = displaySize;
  const height = displaySize;
  const cellSize = width / maze.grid_size;

  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = "#fcf8f1";
  ctx.fillRect(0, 0, width, height);

  for (let row = 0; row < maze.grid_size; row += 1) {
    for (let col = 0; col < maze.grid_size; col += 1) {
      drawBaseCell(ctx, maze, row, col, cellSize);
      drawOverlayCell(ctx, panelState.dynamicGrid[row][col], row, col, cellSize, now);
    }
  }

  drawEndpoints(ctx, maze, cellSize);
}

function drawBaseCell(ctx, maze, row, col, cellSize) {
  const value = maze.grid[row][col];
  const x = col * cellSize;
  const y = row * cellSize;

  if (value === 1) {
    ctx.fillStyle = COLORS.wall;
  } else if (value > 1) {
    ctx.fillStyle = weightColor(value, maze.max_weight);
  } else {
    ctx.fillStyle = COLORS.passage;
  }

  ctx.fillRect(x, y, cellSize, cellSize);
  ctx.strokeStyle = COLORS.passageShadow;
  ctx.lineWidth = Math.max(0.6, cellSize * 0.035);
  ctx.strokeRect(x, y, cellSize, cellSize);
}

function drawOverlayCell(ctx, cell, row, col, cellSize, now) {
  const x = col * cellSize;
  const y = row * cellSize;
  const inset = Math.max(0, cellSize * 0.03);
  const size = Math.max(cellSize - inset * 2, 0.8);
  const radius = Math.max(1, cellSize * 0.12);

  if (cell.visitedAt) {
    const age = Math.max(0, now - cell.visitedAt);
    const alpha = clamp(0.4, 0.92 - age / 950, 0.92);
    ctx.fillStyle = withAlpha(COLORS.visited, alpha);
    roundRect(ctx, x + inset, y + inset, size, size, radius);
    ctx.fill();
  }

  if (cell.pathAt) {
    const age = Math.max(0, now - cell.pathAt);
    if (age >= 0) {
      const alpha = clamp(0.7, 0.78 + age / 260, 1);
      ctx.shadowBlur = Math.max(4, cellSize * 0.46);
      ctx.shadowColor = withAlpha(COLORS.path, 0.7);
      ctx.fillStyle = withAlpha(COLORS.path, alpha);
      roundRect(ctx, x + inset, y + inset, size, size, radius);
      ctx.fill();
      ctx.shadowBlur = 0;
    }
  }
}

function drawEndpoints(ctx, maze, cellSize) {
  drawMarker(ctx, maze.start[1], maze.start[0], cellSize, COLORS.start);
  drawMarker(ctx, maze.goal[1], maze.goal[0], cellSize, COLORS.goal);
}

function drawMarker(ctx, col, row, cellSize, color) {
  const x = col * cellSize;
  const y = row * cellSize;
  const inset = Math.max(0.5, cellSize * 0.08);
  const size = Math.max(cellSize - inset * 2, 1);

  ctx.fillStyle = color;
  roundRect(ctx, x + inset, y + inset, size, size, Math.max(1, cellSize * 0.14));
  ctx.fill();

  ctx.lineWidth = Math.max(1, cellSize * 0.08);
  ctx.strokeStyle = "rgba(255, 255, 255, 0.92)";
  roundRect(ctx, x + inset, y + inset, size, size, Math.max(1, cellSize * 0.14));
  ctx.stroke();
}

function resizeCanvas(canvas, ctx) {
  const ratio = window.devicePixelRatio || 1;
  const displaySize = Math.floor(canvas.clientWidth);
  const pixelSize = Math.floor(displaySize * ratio);
  if (canvas.width === pixelSize && canvas.height === pixelSize) {
    return displaySize;
  }
  canvas.width = pixelSize;
  canvas.height = pixelSize;
  ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
  return displaySize;
}

function weightColor(value, maxWeight) {
  const intensity = maxWeight <= 1 ? 0 : (value - 2) / Math.max(1, maxWeight - 2);
  const red = Math.round(255 - intensity * 42);
  const green = Math.round(225 - intensity * 115);
  const blue = Math.round(176 - intensity * 116);
  return `rgb(${red}, ${green}, ${blue})`;
}

function deriveEventRate(results) {
  const longestTrace = Math.max(...results.map((result) => result.events.length));
  return clamp(DEFAULT_EVENT_RATE, Math.round(longestTrace / 10), 1800);
}

function withAlpha(hex, alpha) {
  const normalized = clamp(0, alpha, 1);
  const bigint = Number.parseInt(hex.slice(1), 16);
  const r = (bigint >> 16) & 255;
  const g = (bigint >> 8) & 255;
  const b = bigint & 255;
  return `rgba(${r}, ${g}, ${b}, ${normalized})`;
}

function roundRect(ctx, x, y, width, height, radius) {
  ctx.beginPath();
  ctx.moveTo(x + radius, y);
  ctx.lineTo(x + width - radius, y);
  ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
  ctx.lineTo(x + width, y + height - radius);
  ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
  ctx.lineTo(x + radius, y + height);
  ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
  ctx.lineTo(x, y + radius);
  ctx.quadraticCurveTo(x, y, x + radius, y);
  ctx.closePath();
}

function clamp(min, value, max) {
  return Math.min(max, Math.max(min, value));
}

function setRunState(message) {
  dom.runStatus.textContent = message;
}

loadRun();
