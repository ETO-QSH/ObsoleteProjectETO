// 游戏状态管理
const GameState = {
    rows: 5,
    cols: 5,
    grid: [], // 0:空，1:绿，2:黄，-1:禁用
    constraints: {
        top: [],    // 从上往下看，绿色可见数
        bottom: [], // 从下往上看，黄色可见数
        left: [],   // 从左往右看，绿色可见数
        right: []   // 从右往左看，黄色可见数
    },
    pieces: [], // 预设拼图块
    activePieces: [], // 使用的拼图块
    solution: null,
    
    // 初始化状态
    init() {
        this.grid = Array(this.rows).fill(null).map(() => Array(this.cols).fill(0));
        this.constraints.top = Array(this.cols).fill(0);
        this.constraints.bottom = Array(this.cols).fill(0);
        this.constraints.left = Array(this.rows).fill(0);
        this.constraints.right = Array(this.rows).fill(0);
    },
    
    // 重置网格
    clearGrid() {
        this.grid = Array(this.rows).fill(null).map(() => Array(this.cols).fill(0));
        this.solution = null;
    },
    
    // 清除解答
    clearSolution() {
        this.solution = null;
    },
    
    // 更新网格尺寸
    resize(newRows, newCols) {
        const oldGrid = this.grid;
        const oldTop = [...this.constraints.top];
        const oldBottom = [...this.constraints.bottom];
        const oldLeft = [...this.constraints.left];
        const oldRight = [...this.constraints.right];
        
        this.rows = Math.min(Math.max(newRows, 3), 10);
        this.cols = Math.min(Math.max(newCols, 3), 10);
        
        // 初始化新网格，尽量保留数据
        this.grid = Array(this.rows).fill(null).map((_, r) => 
            Array(this.cols).fill(null).map((_, c) => 
                r < oldGrid.length && c < oldGrid[0].length ? oldGrid[r][c] : 0
            )
        );
        
        this.constraints.top = Array(this.cols).fill(0).map((_, i) => i < oldTop.length ? oldTop[i] : 0);
        this.constraints.bottom = Array(this.cols).fill(0).map((_, i) => i < oldBottom.length ? oldBottom[i] : 0);
        this.constraints.left = Array(this.rows).fill(0).map((_, i) => i < oldLeft.length ? oldLeft[i] : 0);
        this.constraints.right = Array(this.rows).fill(0).map((_, i) => i < oldRight.length ? oldRight[i] : 0);
    },
    
    // 点击格子循环：空->绿->黄->空
    cycleCell(r, c) {
        if (this.grid[r][c] === -1) return; // 禁用状态不响应左键
        this.grid[r][c] = (this.grid[r][c] + 1) % 3;
    },
    
    // 右键禁用/启用
    toggleDisable(r, c) {
        this.grid[r][c] = this.grid[r][c] === -1 ? 0 : -1;
    },
    
    // 更新约束值
    updateConstraint(type, index, value) {
        this.constraints[type][index] = parseInt(value) || 0;
    }
};

// 预设拼图块模板（1 表示有格子，颜色由 piece.color 决定）
const PieceTemplates = [
    // 单格
    [[1]],
    // 双格
    [[1,1]],
    // L 型
    [[1,0],[1,1]],
    [[1,1],[1,0]],
    // T 型
    [[1,1,1],[0,1,0]],
    // 十字
    [[0,1,0],[1,1,1],[0,1,0]],
];
