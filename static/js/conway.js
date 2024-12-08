class ConwayBackground {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.cellSize = 15;
        this.opacity = 0.3;
        this.fadeSpeed = 0.15;
        this.cells = [];
        this.running = true;
        // Set canvas size to window size
        this.resize();
        window.addEventListener('resize', () => this.resize());
        // Initialize grid
        this.initGrid();
        // Start the animation loop
        this.animate();
        // Add click listener for interaction
        this.canvas.addEventListener('click', (e) => this.handleClick(e));
    }
    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
        this.columns = Math.floor(this.canvas.width / this.cellSize);
        this.rows = Math.floor(this.canvas.height / this.cellSize);
    }
    initGrid() {
        this.cells = new Array(this.columns);
        for (let i = 0; i < this.columns; i++) {
            this.cells[i] = new Array(this.rows);
            for (let j = 0; j < this.rows; j++) {
                // Random initial state with 8% chance of being alive
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
                    // 70% chance to create a cell
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
                    // Cell is alive
                    newCells[i][j] = neighbors === 2 || neighbors === 3;
                } else {
                    // Cell is dead
                    newCells[i][j] = neighbors === 3;
                }
            }
        }
        this.cells = newCells;
    }
    draw() {
        this.ctx.fillStyle = `rgba(0, 0, 0, ${this.fadeSpeed})`;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        this.ctx.fillStyle = `rgba(47, 255, 209, ${this.opacity})`;
        for (let i = 0; i < this.columns; i++) {
            for (let j = 0; j < this.rows; j++) {
                if (this.cells[i][j]) {
                    // Add a gentle glow effect
                    const centerX = i * this.cellSize + this.cellSize / 2;
                    const centerY = j * this.cellSize + this.cellSize / 2;
                    // Create gradient for each cell
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
        // Create a cluster of cells instead of a glider
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
// Initialize when the document is loaded
document.addEventListener('DOMContentLoaded', () => {
    const conway = new ConwayBackground();
});
