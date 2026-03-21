// 求解算法模块 - 使用回溯法解决拼图问题
// 分别对绿色和黄色拼图块进行求解，然后合并结果

const PuzzleSolver = {
    // 生成所有旋转（0°, 90°, 180°, 270°）
    generateRotations(shape) {
        const rotations = [this.deepCopyShape(shape)];
        let current = shape;
        
        for (let i = 0; i < 3; i++) {
            current = this.rotate90(current);
            // 检查是否重复
            const key = JSON.stringify(current);
            if (!rotations.some(r => JSON.stringify(r) === key)) {
                rotations.push(this.deepCopyShape(current));
            }
        }
        
        return rotations;
    },
    
    // 顺时针旋转 90 度
    rotate90(shape) {
        const h = shape.length;
        const w = shape[0].length;
        const res = Array(w).fill(null).map(() => Array(h).fill(0));
        
        for (let r = 0; r < h; r++) {
            for (let c = 0; c < w; c++) {
                res[c][h - 1 - r] = shape[r][c];
            }
        }
        
        return res;
    },
    
    // 深度复制形状
    deepCopyShape(shape) {
        return shape.map(row => [...row]);
    },
    
    // 准备拼图块数据（按颜色分组）
    preparePiecesByColor() {
        const greenPieces = [];
        const yellowPieces = [];
        
        GameState.activePieces.forEach(p => {
            const color = p.color || 1; // 1=绿，2=黄
            const pieceData = {
                id: p.id,
                shape: this.deepCopyShape(p.shape),
                rotations: this.generateRotations(p.shape),
                color: color
            };
            
            if (color === 1) {
                greenPieces.push(pieceData);
            } else {
                yellowPieces.push(pieceData);
            }
        });
        
        return { green: greenPieces, yellow: yellowPieces };
    },
    
// 主求解函数 - 分别求解绿色和黄色
    solve() {
        const startTime = Date.now();
        
        // 准备数据
        const piecesByColor = this.preparePiecesByColor();
        const availableCellsSet = ConstraintValidator.getAvailableCellsSet();
        
        // 获取 01 化的约束网格（用于求解）
        const constraintGrids = ConstraintValidator.getBinaryConstraintGrids();
        
        
        // 先求解绿色拼图
        const greenSolution = [];
        const greenFound = this.backtrack(0, piecesByColor.green, greenSolution, availableCellsSet, constraintGrids.green);
        
        if (!greenFound) {
            return { found: false, timeMs: Date.now() - startTime };
        }
        
        // 更新已占用格子
        const occupiedSet = new Set(availableCellsSet);
        greenSolution.forEach(s => {
            s.cells.forEach(cell => {
                occupiedSet.delete(`${cell.r},${cell.c}`);
            });
        });
        
        // 求解黄色拼图
        const yellowSolution = [];
        const yellowFound = this.backtrackWithOccupied(0, piecesByColor.yellow, yellowSolution, occupiedSet, constraintGrids.yellow);
        
        if (!yellowFound) {
            return { found: false, timeMs: Date.now() - startTime };
        }
        
        // 合并结果
        const fullSolution = [...greenSolution, ...yellowSolution];
        
        // 验证完整约束
        const valid = ConstraintValidator.checkConstraints(fullSolution);
        
        return {
            found: valid,
            solution: valid ? fullSolution : null,
            timeMs: Date.now() - startTime
        };
    },
    
    // 回溯算法（使用颜色约束网格）
    backtrack(pieceIdx, pieces, solution, availableCellsSet, colorGrid) {
        // 所有拼图块都已放置
        if (pieceIdx === pieces.length) {
            return true;
        }
        
        const piece = pieces[pieceIdx];
        
        // 尝试每个旋转
        for (const rot of piece.rotations) {
            const h = rot.length;
            const w = rot[0].length;
            
            // 尝试每个位置
            for (let r = 0; r <= GameState.rows - h; r++) {
                for (let c = 0; c <= GameState.cols - w; c++) {
                    // 检查是否可以放置
                    const placement = ConstraintValidator.checkPlacement(
                        rot, r, c, solution, availableCellsSet, colorGrid
                    );
                    
                    if (placement.valid) {
                        // 放置拼图块
                        solution.push({
                            piece: piece,
                            rotation: rot,
                            r, c,
                            cells: placement.cells
                        });
                        
                        // 递归处理下一个拼图块
                        if (this.backtrack(pieceIdx + 1, pieces, solution, availableCellsSet, colorGrid)) {
                            return true;
                        }
                        
                        // 回溯
                        solution.pop();
                    }
                }
            }
        }
        
        return false;
    },
    
    // 回溯算法（使用已占用集合）
    backtrackWithOccupied(pieceIdx, pieces, solution, occupiedSet, colorGrid) {
        if (pieceIdx === pieces.length) {
            return true;
        }
        
        const piece = pieces[pieceIdx];
        
        for (const rot of piece.rotations) {
            const h = rot.length;
            const w = rot[0].length;
            
            for (let r = 0; r <= GameState.rows - h; r++) {
                for (let c = 0; c <= GameState.cols - w; c++) {
                    // 检查是否可以放置
                    const placement = this.checkPlacementWithOccupied(
                        rot, r, c, solution, occupiedSet, colorGrid
                    );
                    
                    if (placement.valid) {
                        solution.push({
                            piece: piece,
                            rotation: rot,
                            r, c,
                            cells: placement.cells
                        });
                        
                        // 标记为已占用
                        placement.cells.forEach(cell => {
                            occupiedSet.delete(`${cell.r},${cell.c}`);
                        });
                        
                        if (this.backtrackWithOccupied(pieceIdx + 1, pieces, solution, occupiedSet, colorGrid)) {
                            return true;
                        }
                        
                        // 回溯
                        solution.pop();
                        placement.cells.forEach(cell => {
                            occupiedSet.add(`${cell.r},${cell.c}`);
                        });
                    }
                }
            }
        }
        
        return false;
    },
    
    // 检查放置（使用已占用集合）
    checkPlacementWithOccupied(shape, startR, startC, existingSolution, occupiedSet, colorGrid) {
        const cells = [];
        const h = shape.length;
        const w = shape[0].length;
        
        for (let r = 0; r < h; r++) {
            for (let c = 0; c < w; c++) {
                if (shape[r][c] !== 0) {
                    const gr = startR + r;
                    const gc = startC + c;
                    
                    if (gr < 0 || gr >= GameState.rows || gc < 0 || gc >= GameState.cols) {
                        return { valid: false, reason: 'out_of_bounds' };
                    }
                    
                    const cellKey = `${gr},${gc}`;
                    if (!occupiedSet.has(cellKey)) {
                        return { valid: false, reason: 'occupied' };
                    }
                    
                    // 检查颜色约束
                    if (colorGrid && colorGrid[gr][gc] !== 1) {
                        return { valid: false, reason: 'color_constraint' };
                    }
                    
                    // 检查预填充颜色
                    const fixedColor = ConstraintValidator.getFixedColor(gr, gc);
                    if (fixedColor !== 0 && fixedColor !== shape[r][c]) {
                        return { valid: false, reason: 'color_mismatch' };
                    }
                    
                    cells.push({ r: gr, c: gc, color: shape[r][c] });
                }
            }
        }
        
        return { valid: true, cells };
    },
    
    // 带进度显示的求解
    solveWithProgress() {
        return new Promise((resolve) => {
            setTimeout(() => {
                const result = this.solve();
                resolve(result);
            }, 50);
        });
    }
};

// 供 HTML 调用的验证和求解函数
function validateAndSolve() {
    // 1. 基础验证
    if (GameState.activePieces.length === 0) {
        UIToast.show('请至少添加一个拼图块到任务盒子');
        return;
    }
    
    // 2. 约束验证
    const constraintResult = ConstraintValidator.validate();
    if (!constraintResult.valid) {
        UIToast.show(`约束冲突：<br>${constraintResult.conflicts.slice(0, 3).join('<br>')}`);
        return;
    }
    
    // 3. 基础条件验证
    const basicCheck = ConstraintValidator.validateBasics();
    if (!basicCheck.valid) {
        UIToast.show(basicCheck.message);
        return;
    }
    
    // 4. 开始求解
    SolverUI.startSolving();
}

// 求解 UI 管理
const SolverUI = {
    startSolving() {
        const statusEl = document.getElementById('solverStatus');
        const stepsEl = document.getElementById('solutionSteps');
        
        if (statusEl) {
            statusEl.innerHTML = '<span class="text-cyan-400 animate-pulse">求解中...</span>';
        }
        if (stepsEl) {
            stepsEl.innerHTML = '';
        }
        
        PuzzleSolver.solveWithProgress().then(result => {
            this.showResult(result);
        });
    },
    
    showResult(result) {
        const statusEl = document.getElementById('solverStatus');
        
        if (result.found) {
            if (statusEl) {
                statusEl.innerHTML = `<span class="text-emerald-400">✓ 找到解答！耗时${result.timeMs}ms</span>`;
            }
            
            GameState.solution = result.solution;
            MainGridRenderer.render();
            SolutionRenderer.display(result.solution);
        } else {
            if (statusEl) {
                statusEl.innerHTML = `<span class="text-red-400">✗ 无解（耗时${result.timeMs}ms）</span>`;
            }
            UIToast.show('未找到满足所有约束的解答，请调整拼图块或约束');
            GameState.solution = null;
        }
    }
};