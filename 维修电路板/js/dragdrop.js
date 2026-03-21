// 拖拽功能模块

const DragDropManager = {
    draggedElement: null,
    source: null,
    
    // 初始化拖拽功能
    init() {
        this.setupGlobalListeners();
    },
    
    // 设置全局监听器
    setupGlobalListeners() {
        // 使用事件委托处理动态元素
        document.addEventListener('dragstart', (e) => {
            const draggable = e.target.closest('[draggable="true"]');
            if (draggable) {
                this.draggedElement = draggable;
                this.source = draggable.dataset.source;
                draggable.classList.add('dragging');
                e.dataTransfer.effectAllowed = 'move';
            }
        });
        
        document.addEventListener('dragend', (e) => {
            const draggable = e.target.closest('[draggable="true"]');
            if (draggable) {
                draggable.classList.remove('dragging');
            }
            this.draggedElement = null;
            this.source = null;
        });
        
        // 放置区域事件
        const activeZone = document.getElementById('activePieces');
        if (activeZone) {
            activeZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                activeZone.classList.add('drop-zone');
                e.dataTransfer.dropEffect = 'move';
            });
            
            activeZone.addEventListener('dragleave', (e) => {
                // 只有当离开的是放置区域本身时才移除样式
                if (e.target === activeZone) {
                    activeZone.classList.remove('drop-zone');
                }
            });
            
            activeZone.addEventListener('drop', (e) => {
                e.preventDefault();
                activeZone.classList.remove('drop-zone');
                this.handleDrop();
            });
        }
    },
    
    // 处理放置
    handleDrop() {
        const pieceId = this.draggedElement?.dataset.pieceId;
        if (!pieceId) return;
        
        if (this.source === 'library') {
            this.addFromLibrary(pieceId);
        } else if (this.source === 'active') {
            // 可以处理在盒子内重新排序
            const index = parseInt(this.draggedElement.dataset.index);
            // 目前简单处理：不做任何事（已经在盒子里了）
        }
    },
    
    // 从库中添加拼图块（深拷贝，切断联系）
    addFromLibrary(pieceId) {
        const piece = GameState.pieces.find(p => p.id === pieceId);
        if (!piece) return;
        
        const pieceColor = piece.color || 1;
        const pieceShapeKey = JSON.stringify(piece.shape);
        
        // 检查是否已存在相同形状和颜色的拼图块
        const existing = GameState.activePieces.find(p => {
            const sameColor = (p.color || 1) === pieceColor;
            const sameShape = JSON.stringify(p.shape) === pieceShapeKey;
            return sameColor && sameShape;
        });
        
        if (existing) {
            // 相同拼图块，数量加一
            existing.count = (existing.count || 1) + 1;
        } else {
            // 新拼图块，深拷贝
            const newPiece = {
                id: `${pieceId}_copy_${Date.now()}`,
                shape: piece.shape.map(row => [...row]),
                name: piece.name,
                count: 1,
                color: pieceColor
            };
            GameState.activePieces.push(newPiece);
        }
        
        ActivePiecesRenderer.render();
    },
    
    // 从盒子中移除拼图块（供外部调用）
    removeFromBox(index) {
        PieceManager.removeActivePiece(index);
    }
};

// 供 HTML 调用的函数
function addNewPiece() {
    PieceManager.addNewPiece();
}

function setupDragAndDrop() {
    // 初始化拖拽（现在由 DragDropManager.init() 处理）
}