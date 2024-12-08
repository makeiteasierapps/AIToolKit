class ConwayBackground {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.cellSize = 15;
        this.opacity = 0.3;
        this.fadeSpeed = 0.15;
        this.cells = [];
        this.running = true;
        // Initialize canvas size
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
        this.columns = Math.floor(this.canvas.width / this.cellSize);
        this.rows = Math.floor(this.canvas.height / this.cellSize);
        // Set up resize handling with debounce
        this.lastResizeTime = 0;
        this.resizeThrottleDelay = 16; // About 60fps
        window.addEventListener('resize', () => this.throttledResize());

        this.initGrid();
        this.animate();
        this.canvas.addEventListener('click', (e) => this.handleClick(e));
    }
    throttledResize() {
        const now = Date.now();
        if (now - this.lastResizeTime >= this.resizeThrottleDelay) {
            this.lastResizeTime = now;
            this.handleResize();
        }
    }
    handleResize() {
        // Store old dimensions and cells
        const oldCells = this.cells;
        const oldColumns = this.columns;
        const oldRows = this.rows;
        // Update canvas size
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
        this.columns = Math.floor(this.canvas.width / this.cellSize);
        this.rows = Math.floor(this.canvas.height / this.cellSize);
        // Only recreate grid if dimensions actually changed
        if (this.columns !== oldColumns || this.rows !== oldRows) {
            // Reuse existing array when possible
            if (!this.cells || this.cells.length !== this.columns) {
                this.cells = new Array(this.columns);
            }
            // Efficient array initialization
            for (let i = 0; i < this.columns; i++) {
                if (!this.cells[i] || this.cells[i].length !== this.rows) {
                    this.cells[i] = new Array(this.rows);
                }
                for (let j = 0; j < this.rows; j++) {
                    if (i < oldColumns && j < oldRows) {
                        // Preserve existing cells
                        this.cells[i][j] = oldCells[i][j];
                    } else {
                        // Initialize new cells with lower probability
                        this.cells[i][j] = Math.random() < 0.03;
                    }
                }
            }
        }
        // Force immediate redraw
        this.draw();
    }
    initGrid() {
        this.cells = new Array(this.columns);
        for (let i = 0; i < this.columns; i++) {
            this.cells[i] = new Array(this.rows);
            for (let j = 0; j < this.rows; j++) {
                this.cells[i][j] = Math.random() < 0.08;
            }
        }
    }
    createCells(x, y, radius = 2) {
        for (let i = -radius; i <= radius; i++) {
            for (let j = -radius; j <= radius; j++) {
                const col = (x + i + this.columns) % this.columns;
                const row = (y + j + this.rows) % this.rows;
                if (Math.random() < 0.7) {
                    this.cells[col][row] = true;
                }
            }
        }
    }
    getNeighbors(x, y) {
        let count = 0;
        for (let i = -1; i <= 1; i++) {
            for (let j = -1; j <= 1; j++) {
                if (i === 0 && j === 0) continue;
                let col = (x + i + this.columns) % this.columns;
                let row = (y + j + this.rows) % this.rows;
                if (this.cells[col][row]) {
                    count++;
                }
            }
        }
        return count;
    }
    update() {
        let newCells = new Array(this.columns);
        for (let i = 0; i < this.columns; i++) {
            newCells[i] = new Array(this.rows);
            for (let j = 0; j < this.rows; j++) {
                let neighbors = this.getNeighbors(i, j);
                if (this.cells[i][j]) {
                    newCells[i][j] = neighbors === 2 || neighbors === 3;
                } else {
                    newCells[i][j] = neighbors === 3;
                }
            }
        }
        this.cells = newCells;
    }
    draw() {
        this.ctx.fillStyle = `rgba(0, 0, 0, ${this.fadeSpeed})`;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        for (let i = 0; i < this.columns; i++) {
            for (let j = 0; j < this.rows; j++) {
                if (this.cells[i][j]) {
                    const centerX = i * this.cellSize + this.cellSize / 2;
                    const centerY = j * this.cellSize + this.cellSize / 2;
                    const gradient = this.ctx.createRadialGradient(
                        centerX,
                        centerY,
                        0,
                        centerX,
                        centerY,
                        this.cellSize
                    );
                    gradient.addColorStop(
                        0,
                        `rgba(47, 255, 209, ${this.opacity})`
                    );
                    gradient.addColorStop(1, 'rgba(47, 255, 209, 0)');
                    this.ctx.fillStyle = gradient;
                    this.ctx.beginPath();
                    this.ctx.arc(
                        centerX,
                        centerY,
                        this.cellSize / 2,
                        0,
                        Math.PI * 2
                    );
                    this.ctx.fill();
                }
            }
        }
    }
    handleClick(event) {
        const rect = this.canvas.getBoundingClientRect();
        const x = Math.floor((event.clientX - rect.left) / this.cellSize);
        const y = Math.floor((event.clientY - rect.top) / this.cellSize);
        this.createCells(x, y, 3);
    }
    animate() {
        if (this.running) {
            this.update();
            this.draw();
            setTimeout(() => requestAnimationFrame(() => this.animate()), 100);
        }
    }
    stop() {
        this.running = false;
    }
    start() {
        if (!this.running) {
            this.running = true;
            this.animate();
        }
    }
}
document.addEventListener('DOMContentLoaded', () => {
    const conway = new ConwayBackground();
});
