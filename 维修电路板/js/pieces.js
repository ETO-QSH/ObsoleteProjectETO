// 拼图块管理模块

const PieceManager = {
    // 生成预设拼图块
    generatePresetPieces() {
        GameState.pieces = PieceTemplates.map((template, idx) => ({
            id: `preset_${idx}`,
            shape: template.map(row => [...row]),
            name: `元件${idx + 1}`
        }));
    },
    
    // 添加新拼图块
    addNewPiece() {
        const id = `custom_${Date.now()}`;
        GameState.pieces.push({
            id: id,
            shape: [[1]],
            name: `自定义${GameState.pieces.length + 1}`
        });
        // 延迟渲染，等待其他模块加载
        setTimeout(() => {
            PieceLibraryRenderer.render();
            ActivePiecesRenderer.render();
        }, 0);
    },
    
    // 删除拼图块
    deletePiece(id) {
        GameState.pieces = GameState.pieces.filter(p => p.id !== id);
        GameState.activePieces = GameState.activePieces.filter(p => p.id !== id);
        setTimeout(() => {
            PieceLibraryRenderer.render();
            ActivePiecesRenderer.render();
        }, 0);
    },
    
    // 切换整个拼图块的颜色（1=绿，2=黄）
    togglePieceColor(pieceId, event) {
        event.stopPropagation();
        const piece = GameState.pieces.find(p => p.id === pieceId) || 
                      GameState.activePieces.find(p => p.id === pieceId);
        if (!piece) return;
        
        // 切换拼图块的 color 属性（1=绿，2=黄）
        piece.color = piece.color === 2 ? 1 : 2;
        
        // 重新渲染
        PieceLibraryRenderer.render();
        ActivePiecesRenderer.render();
    },
    
    // 从盒子移除拼图块（×按钮直接移除整个拼图块）
    removeActivePiece(index) {
        GameState.activePieces.splice(index, 1);
        ActivePiecesRenderer.render();
    },
    
    // 计算拼图块中的颜色数量
    countColors() {
        let greenPieces = 0, yellowPieces = 0;
        GameState.activePieces.forEach(piece => {
            const count = piece.count || 1;
            piece.shape.forEach(row => {
                row.forEach(cell => {
                    if (cell === 1) greenPieces += count;
                    if (cell === 2) yellowPieces += count;
                });
            });
        });
        return { green: greenPieces, yellow: yellowPieces };
    },
    
    // 获取拼图块总格数
    getTotalCells() {
        let total = 0;
        GameState.activePieces.forEach(piece => {
            const count = piece.count || 1;
            piece.shape.forEach(row => {
                row.forEach(cell => {
                    if (cell !== 0) total += count;
                });
            });
        });
        return total;
    }
};

// 拼图块预览渲染
const PiecePreviewRenderer = {
    // 渲染单个拼图块预览
    render(piece, editable = true, isInActive = false, source = null) {
        const width = piece.shape[0].length;
        // 根据拼图块的 color 属性决定整体颜色类名（1=绿，2=黄）
        const colorClass = piece.color === 2 ? 'yellow-piece' : 'green-piece';
        
        // 库中拼图块：可拖拽，点击切换颜色
        // 任务盒子中拼图块：不可拖拽（外层容器拖拽），点击切换颜色
        const draggableAttr = source === 'library' ? `draggable="true" data-piece-id="${piece.id}" data-source="library"` : '';
        const cursorClass = source === 'library' ? 'cursor-move' : '';
        
        return `
            <div class="piece-preview-wrapper ${colorClass} ${cursorClass}"
                 ${editable ? `onclick="PieceManager.togglePieceColor('${piece.id}', event)"` : ''}
                 ${draggableAttr}>
                <div class="piece-preview-grid" 
                     style="grid-template-columns: repeat(${width}, 24px);">
                    ${piece.shape.map((row, r) => 
                        row.map((cell, c) => {
                            if (cell === 0) return `<div class="w-6 h-6"></div>`;
                            // 单元格不需要颜色类，由父容器统一控制
                            return `<div class="piece-cell w-6 h-6 rounded-sm border border-slate-600/50"></div>`;
                        }).join('')
                    ).join('')}
                </div>
            </div>
        `;
    }
};

// 拼图块库渲染
const PieceLibraryRenderer = {
    render() {
        const container = document.getElementById('pieceLibrary');
        if (!container) return;
        
        container.innerHTML = GameState.pieces.map((piece, idx) => `
            <div class="piece-item bg-slate-900/50 p-3 rounded-xl border border-slate-700 hover:border-cyan-500 transition-all">
                <div class="flex justify-between items-center mb-2">
                    <span class="text-xs font-bold text-slate-400">${piece.name}</span>
                    <button onclick="PieceManager.deletePiece('${piece.id}')" class="text-red-400 hover:text-red-300 text-xs">×</button>
                </div>
                <div class="flex justify-center">
                    ${PiecePreviewRenderer.render(piece, true, false, 'library')}
                </div>
            </div>
        `).join('');
    }
};

// 使用中的拼图块渲染
const ActivePiecesRenderer = {
    render() {
        const container = document.getElementById('activePieces');
        if (!container) return;
        
        if (GameState.activePieces.length === 0) {
            container.innerHTML = '<p class="text-slate-500 text-sm text-center py-8">将上方拼图块拖放到这里</p>';
            return;
        }
        
        container.innerHTML = GameState.activePieces.map((piece, idx) => `
            <div class="bg-slate-900/50 p-3 rounded-xl border border-slate-700 hover:border-cyan-500 transition-all">
                <div class="flex justify-between items-center mb-2">
                    <span class="text-xs font-bold text-slate-400">数量：${piece.count || 1}</span>
                    <button onclick="PieceManager.removeActivePiece(${idx}); event.stopPropagation();" class="text-red-400 hover:text-red-300 text-xs">×</button>
                </div>
                <div class="flex justify-center">
                    ${PiecePreviewRenderer.render(piece, false, true, 'active')}
                </div>
                <div class="flex items-center gap-2 justify-center mt-2">
                    <button onclick="event.stopPropagation(); ActivePiecesRenderer.adjustCount(${idx}, -1)" class="w-6 h-6 bg-slate-700 hover:bg-slate-600 rounded flex items-center justify-center text-slate-300 transition-colors">
                        <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z"/></svg>
                    </button>
                    <span class="text-xs text-slate-400 min-w-[40px] text-center">${piece.count || 1}</span>
                    <button onclick="event.stopPropagation(); ActivePiecesRenderer.adjustCount(${idx}, 1)" class="w-6 h-6 bg-slate-700 hover:bg-slate-600 rounded flex items-center justify-center text-slate-300 transition-colors">
                        <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"/></svg>
                    </button>
                </div>
            </div>
        `).join('');
    },
    
    // 调整数量
    adjustCount(index, delta) {
        const piece = GameState.activePieces[index];
        if (!piece) return;
        
        const newCount = (piece.count || 1) + delta;
        if (newCount <= 0) {
            GameState.activePieces.splice(index, 1);
        } else {
            piece.count = newCount;
        }
        this.render();
    }
};

// 合并渲染器（为了兼容性）
const GridRenderer = {
    renderPieceLibrary: () => PieceLibraryRenderer.render(),
    renderAll: () => {
        PieceLibraryRenderer.render();
        ActivePiecesRenderer.render();
        // 延迟调用其他渲染器（它们在 grid.js 中定义）
        setTimeout(() => {
            if (typeof ConstraintRenderer !== 'undefined') ConstraintRenderer.render();
            if (typeof MainGridRenderer !== 'undefined') MainGridRenderer.render();
            if (typeof ConstraintCounter !== 'undefined') ConstraintCounter.update();
        }, 0);
    }
};