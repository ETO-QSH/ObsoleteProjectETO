// 网格渲染和管理模块

const MainGridRenderer = {
    // 渲染主网格
    render() {
        const grid = document.getElementById('mainGrid');
        if (!grid) return;
        
        grid.style.gridTemplateColumns = `repeat(${GameState.cols}, 40px)`;
        
        grid.innerHTML = GameState.grid.map((row, r) => 
            row.map((cell, c) => {
                let bgClass = 'bg-slate-700/50 hover:bg-slate-600/50';
                let content = '';
                
                if (cell === 1) {
                    bgClass = 'bg-emerald-500/80 neon-green';
                    content = '';
                } else if (cell === 2) {
                    bgClass = 'bg-amber-400/80 neon-yellow';
                    content = '';
                } else if (cell === -1) {
                    bgClass = 'bg-slate-800 disabled-cell';
                    content = '<div class="w-full h-full flex items-center justify-center"><span class="text-slate-500 text-lg font-bold">×</span></div>';
                }
                
                return `
                    <div class="grid-cell w-10 h-10 ${bgClass} rounded-lg cursor-pointer flex items-center justify-center border border-slate-600/30 relative"
                         onclick="MainGridRenderer.handleCellClick(${r}, ${c})"
                         data-r="${r}" data-c="${c}">
                        ${content}
                        ${GameState.solution ? SolutionRenderer.renderPiece(r, c) : ''}
                    </div>
                `;
            }).join('')
        ).join('');
    },
    
    // 处理格子点击：禁->绿->黄->空
    handleCellClick(r, c) {
        const cell = GameState.grid[r][c];
        // 循环：0(空) -> -1(禁) -> 1(绿) -> 2(黄) -> 0(空)
        if (cell === -1) {
            GameState.grid[r][c] = 1;
        } else if (cell === 1) {
            GameState.grid[r][c] = 2;
        } else if (cell === 2) {
            GameState.grid[r][c] = 0;
        } else {
            GameState.grid[r][c] = -1;
        }
        this.render();
        // 触发约束重新计算
        ConstraintCounter.update();
    }
};

// 约束输入渲染 - 使用自定义箭头按钮
const ConstraintRenderer = {
    render() {
        this.renderTop();
        this.renderBottom();
        this.renderLeft();
        this.renderRight();
    },
    
    // 生成带自定义箭头的约束输入框 HTML（左右箭头布局 + 可输入文本框）
    createConstraintInput(value, max, colorClass, position, index) {
        // 空值时显示 "-"
        const displayValue = value === '' || value === 0 ? '-' : value;
        return `
            <div class="constraint-wrapper ${colorClass}" data-pos="${position}" data-idx="${index}">
                <button class="arrow-btn arrow-left" onclick="ConstraintRenderer.adjustValue('${position}', ${index}, -1)">
                    <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z"/></svg>
                </button>
                <input type="text" class="constraint-input-value" value="${displayValue}" 
                       onchange="ConstraintRenderer.handleInputChange('${position}', ${index}, this.value)"
                       onclick="this.select()">
                <button class="arrow-btn arrow-right" onclick="ConstraintRenderer.adjustValue('${position}', ${index}, 1)">
                    <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"/></svg>
                </button>
            </div>
        `;
    },
    
    renderTop() {
        const container = document.getElementById('topConstraints');
        if (!container) return;
        
        container.innerHTML = 
            '<div class="w-[40px]"></div>' + 
            GameState.constraints.top.map((v, i) => this.createConstraintInput(v, GameState.rows, 'green', 'top', i)).join('') + 
            '<div class="w-[40px]"></div>';
    },
    
    renderBottom() {
        const container = document.getElementById('bottomConstraints');
        if (!container) return;
        
        container.innerHTML = 
            '<div class="w-[40px]"></div>' + 
            GameState.constraints.bottom.map((v, i) => this.createConstraintInput(v, GameState.rows, 'yellow', 'bottom', i)).join('') + 
            '<div class="w-[40px]"></div>';
    },
    
    renderLeft() {
        const container = document.getElementById('leftConstraints');
        if (!container) return;
        
        container.innerHTML = '<div class="h-[5px]"></div>' +
            GameState.constraints.left.map((v, i) => this.createConstraintInput(v, GameState.cols, 'green', 'left', i)).join('');
    },
    
    renderRight() {
        const container = document.getElementById('rightConstraints');
        if (!container) return;
        
        container.innerHTML = '<div class="h-[5px]"></div>' +
            GameState.constraints.right.map((v, i) => this.createConstraintInput(v, GameState.cols, 'yellow', 'right', i)).join('');
    },
    
    // 调整约束值
    adjustValue(position, index, delta) {
        const constraints = GameState.constraints[position];
        let newValue = (constraints[index] || 0) + delta;
        
        // 循环：0 -> 1 -> 2 -> ... -> max -> 0
        const max = position === 'top' || position === 'bottom' ? GameState.rows : GameState.cols;
        if (newValue > max) newValue = 0;
        if (newValue < 0) newValue = max;
        
        GameState.updateConstraint(position, index, newValue === 0 ? '' : newValue);
        ConstraintCounter.update();
        this.render();
    },
    
    // 处理手动输入
    handleInputChange(position, index, value) {
        const numValue = parseInt(value) || 0;
        const max = position === 'top' || position === 'bottom' ? GameState.rows : GameState.cols;
        const finalValue = Math.max(0, Math.min(max, numValue));
        
        GameState.updateConstraint(position, index, finalValue === 0 ? '' : finalValue);
        ConstraintCounter.update();
        this.render();
    }
};

// 解答渲染
const SolutionRenderer = {
    renderPiece(r, c) {
        if (!GameState.solution) return '';
        return '';
    },
    
    // 显示完整解答
    display(solution) {
        solution.forEach((s, idx) => {
            setTimeout(() => {
                s.cells.forEach(cell => {
                    const el = document.querySelector(`.grid-cell[data-r="${cell.r}"][data-c="${cell.c}"]`);
                    if (el) {
                        el.classList.add('placing');
                        el.classList.add('solution-highlight');
                    }
                });
            }, idx * 100);
        });
        
        // 添加图例
        const legend = document.createElement('div');
        legend.className = 'mt-4 p-4 bg-slate-800/80 rounded-xl text-sm';
        legend.innerHTML = '<h4 class="font-bold mb-2 text-cyan-400">解答详情</h4>' + 
            solution.map((s, i) => `
                <div class="flex items-center gap-2 mb-1">
                    <span class="text-slate-500">#${i+1}</span>
                    <span class="text-emerald-400">${s.piece.id.split('_')[0]}</span>
                    <span class="text-slate-400">位置：(${s.r},${s.c})</span>
                </div>
            `).join('');
        
        const statusEl = document.getElementById('solverStatus');
        if (statusEl && !statusEl.querySelector('.mt-4')) {
            statusEl.appendChild(legend);
        }
    }
};

// 约束计数器 - 显示所有解
const ConstraintCounter = {
    update() {
        // 更新所有解
        this.renderAllSolutions();
    },
    
    // 渲染所有解（离散分布居中，2:1:2 弹簧，自动滚动）
    renderAllSolutions() {
        const solutionsEl = document.getElementById('solutionSteps');
        if (!solutionsEl) return;
        
        const allSolutions = ConstraintValidator.getAllValidSolutions();
        
        if (allSolutions.length === 0) {
            solutionsEl.innerHTML = '<p class="text-slate-500 text-xs">暂无有效解</p>';
            return;
        }
        
        // 计算每个解网格的宽度（像素）
        const cellSize = 12; // 每个格子 12px
        const gap = 2; // 格子间距 2px
        const padding = 8; // 解网格内边距 8px
        const labelHeight = 20; // 标签高度
        const rowGap = 8; // 行间距
        const solWidth = GameState.cols * (cellSize + gap) - gap + padding * 2;
        const solHeight = GameState.rows * (cellSize + gap) - gap + padding * 2 + labelHeight;
        
        // 计算容器宽度（减去内边距）
        const constraintBox = document.getElementById('constraintStatusBox');
        const containerWidth = constraintBox ? (constraintBox.clientWidth - 45) : 300;
        
        // 计算每行能放多少个解（考虑弹簧间距）
        const solsPerRow = Math.max(1, Math.floor(containerWidth / solWidth));
        
        // 计算总行数
        const totalRows = Math.ceil(allSolutions.length / solsPerRow);
        
        // 计算可用高度（约束框高度 - 标题高度 - 状态栏高度 - 上下边距）
        const availableHeight = (constraintBox ? constraintBox.clientHeight : 400) - 108;
        
        // 构建 HTML
        let html = '';
        
        // 标题行：标题 + 解计数（右下角）
        html += `<div class="flex justify-between items-center mb-3">
            <span class="text-xs text-slate-500">约束解列表：</span>
            <span class="text-[10px] text-slate-500">共 ${allSolutions.length} 个解</span>
        </div>`;
        
        // 解网格容器 - 使用 CSS grid 实现 2:1:2 弹簧分布
        // 按行分组渲染
        html += `<div class="flex flex-col" style="max-height: ${availableHeight}px; overflow-y: auto; padding: ${rowGap}px 0;">`;
        
        // 显示所有解
        for (let row = 0; row < totalRows; row++) {
            const rowSolutions = allSolutions.slice(row * solsPerRow, Math.min((row + 1) * solsPerRow, allSolutions.length));
            const actualSolsInRow = rowSolutions.length;

            const totalSolWidth = actualSolsInRow * solWidth;
            const remainingWidth = containerWidth - totalSolWidth;
            const numGaps = actualSolsInRow + 1; // 左右两边 + 中间的间隔数
            const springUnit = remainingWidth / numGaps;
            
            // 每行格式：[x][sol][x][sol][x]...[sol][x]
            html += `<div class="flex items-center" style="flex-shrink: 0; margin: ${rowGap}px 0;">`;
            
            // 左弹簧 x
            html += `<div style="flex: 1 0 0; min-width: ${springUnit}px;"></div>`;
            
            rowSolutions.forEach((sol, idx) => {
                const gridCells = sol.map(row => 
                    row.map(cell => {
                        let bgClass = 'bg-slate-700';
                        if (cell === 1) bgClass = 'bg-emerald-500';
                        else if (cell === 2) bgClass = 'bg-amber-400';
                        return `<div class="w-3 h-3 rounded-sm ${bgClass}"></div>`;
                    }).join('')
                ).join('');
                
                const isLastInRow = idx === actualSolsInRow - 1;
                
                html += `
                    <div class="p-2 bg-slate-800/50 rounded border border-slate-700 flex-shrink-0" style="width: ${solWidth}px;">
                        <p class="text-xs text-slate-400 mb-1 text-center">解 ${row * solsPerRow + idx + 1}</p>
                        <div class="grid gap-0.5" style="grid-template-columns: repeat(${GameState.cols}, 12px);">
                            ${gridCells}
                        </div>
                    </div>
                `;
                
                // 解间弹簧 / 右弹簧（不是最后一个解时添加中间弹簧，最后一个解后添加右弹簧）
                if (!isLastInRow) {
                    html += `<div style="flex: 1 0 0; min-width: ${springUnit}px;"></div>`;
                }
            });
            
            // 右弹簧 x
            html += `<div style="flex: 1 0 0; min-width: ${springUnit}px;"></div>`;
            
            html += `</div>`;
        }
        
        html += '</div>';
        
        // 设置容器样式
        solutionsEl.style.position = 'relative';
        solutionsEl.innerHTML = html;
    }
};

// 同步约束状态框高度与主游戏区域
function syncConstraintBoxHeight() {
    const gameGrid = document.querySelector('.bg-slate-900\\/80.rounded-2xl');
    const constraintBox = document.getElementById('constraintStatusBox');
    if (gameGrid && constraintBox) {
        const height = gameGrid.offsetHeight;
        constraintBox.style.height = `${height}px`;
    }
}

// 更新网格尺寸（供 HTML 调用）
function updateGridSize() {
    const newRows = parseInt(document.getElementById('gridRows').value) || 5;
    const newCols = parseInt(document.getElementById('gridCols').value) || 5;
    
    GameState.resize(newRows, newCols);
    MainGridRenderer.render();
    ConstraintRenderer.render();
    ConstraintCounter.update();
    
    // 同步高度
    setTimeout(syncConstraintBoxHeight, 50);
}

// 清空网格（供 HTML 调用）
function clearGrid() {
    GameState.clearGrid();
    MainGridRenderer.render();
}

// 清除解答（供 HTML 调用）
function clearSolution() {
    GameState.clearSolution();
    MainGridRenderer.render();
    const statusEl = document.getElementById('solverStatus');
    if (statusEl) statusEl.innerHTML = '等待开始...';
}