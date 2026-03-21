// UI 交互模块

const UIToast = {
    element: null,
    messageElement: null,
    timeoutId: null,
    
    // 初始化
    init() {
        this.element = document.getElementById('toast');
        this.messageElement = document.getElementById('toastMessage');
    },
    
    // 显示提示
    show(message, duration = 3000) {
        if (!this.element || !this.messageElement) {
            this.init();
        }
        
        if (this.messageElement) {
            this.messageElement.textContent = message;
        }
        
        if (this.element) {
            this.element.classList.remove('translate-x-full');
            this.element.classList.add('toast-enter');
        }
        
        // 清除之前的定时器
        if (this.timeoutId) {
            clearTimeout(this.timeoutId);
        }
        
        // 设置新的定时器
        this.timeoutId = setTimeout(() => {
            this.hide();
        }, duration);
    },
    
    // 隐藏提示
    hide() {
        if (this.element) {
            this.element.classList.add('translate-x-full');
            this.element.classList.remove('toast-enter');
        }
    }
};

// 初始化函数
function init() {
    // 初始化状态
    GameState.init();
    
    // 生成预设拼图块
    PieceManager.generatePresetPieces();
    
    // 渲染所有组件
    GridRenderer.renderAll();
    
    // 初始化拖拽
    DragDropManager.init();
    
    // 初始化 Toast
    UIToast.init();
    
    // 初始显示约束网格
    ConstraintCounter.update();
    
    // 同步约束状态框高度
    setTimeout(syncConstraintBoxHeight, 100);
    
    console.log('光之拼图 - 约束求解系统已启动');
}

// 启动应用
document.addEventListener('DOMContentLoaded', init);

// 窗口大小改变时同步高度
window.addEventListener('resize', () => setTimeout(syncConstraintBoxHeight, 50));

// 导出供全局使用的函数（为了 HTML 中的 onclick 属性）
window.GameState = GameState;
window.PieceTemplates = PieceTemplates;
window.PieceManager = PieceManager;
window.PiecePreviewRenderer = PiecePreviewRenderer;
window.PieceLibraryRenderer = PieceLibraryRenderer;
window.ActivePiecesRenderer = ActivePiecesRenderer;
window.GridRenderer = GridRenderer;
window.MainGridRenderer = MainGridRenderer;
window.ConstraintRenderer = ConstraintRenderer;
window.SolutionRenderer = SolutionRenderer;
window.ConstraintCounter = ConstraintCounter;
window.ConstraintValidator = ConstraintValidator;
window.PuzzleSolver = PuzzleSolver;
window.SolverUI = SolverUI;
window.DragDropManager = DragDropManager;
window.UIToast = UIToast;

// 全局函数
window.updateGridSize = updateGridSize;
window.clearGrid = clearGrid;
window.clearSolution = clearSolution;
window.validateAndSolve = validateAndSolve;
window.addNewPiece = addNewPiece;
window.setupDragAndDrop = setupDragAndDrop;
window.syncConstraintBoxHeight = syncConstraintBoxHeight;
