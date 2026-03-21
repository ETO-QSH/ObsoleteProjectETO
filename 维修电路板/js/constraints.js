// 约束管理模块 - 根据约束数字生成约束网格
// 参考 Python 实现：枚举所有可能解，找出确定性格子

const ConstraintValidator = {
    // 生成所有可能的网格（根据行列约束）
    // value: 1=绿色，2=黄色
    // initial: 预填充网格
    generatePossibleGrids(rowCounts, colCounts, n, m, value, initial) {
        const forcedMust = new Set(); // 必须填充的位置
        const forcedZero = new Set(); // 必须为空的位置
        
        // 处理预填充
        for (let i = 0; i < n; i++) {
            for (let j = 0; j < m; j++) {
                if (initial[i][j] === value) {
                    forcedMust.add(`${i},${j}`);
                } else if (initial[i][j] === 1 || initial[i][j] === 2 || initial[i][j] === -1) {
                    // 其他颜色或禁用区域不能填充当前颜色
                    forcedZero.add(`${i},${j}`);
                }
            }
        }
        
        // 检查行约束是否可能满足
        for (let i = 0; i < n; i++) {
            const mustInRow = [...forcedMust].filter(k => k.startsWith(`${i},`)).length;
            const zeroInRow = [...forcedZero].filter(k => k.startsWith(`${i},`)).length;
            if (mustInRow > rowCounts[i] || m - zeroInRow < rowCounts[i]) {
                return [];
            }
        }
        
        // 检查列约束是否可能满足
        for (let j = 0; j < m; j++) {
            const mustInCol = [...forcedMust].filter(k => k.endsWith(`,${j}`)).length;
            const zeroInCol = [...forcedZero].filter(k => k.endsWith(`,${j}`)).length;
            if (mustInCol > colCounts[j] || n - zeroInCol < colCounts[j]) {
                return [];
            }
        }
        
        // 计算每行可能的填充位置组合
        const rowPoss = [];
        for (let i = 0; i < n; i++) {
            const mustInRow = [...forcedMust].filter(k => k.startsWith(`${i},`));
            const available = [];
            for (let j = 0; j < m; j++) {
                const key = `${i},${j}`;
                if (!forcedMust.has(key) && !forcedZero.has(key)) {
                    available.push(j);
                }
            }
            const needCount = rowCounts[i] - mustInRow.length;
            if (needCount < 0 || needCount > available.length) {
                return [];
            }
            rowPoss.push(this.getCombinations(available, needCount));
        }
        
        // 构建所有可能的网格
        const validGrids = [];
        this.buildGrids(0, n, m, rowPoss, forcedMust, value, validGrids);
        
        // 过滤：检查列约束
        const filteredGrids = validGrids.filter(grid => {
            for (let j = 0; j < m; j++) {
                let colSum = 0;
                for (let i = 0; i < n; i++) {
                    if (grid[i][j] === value) colSum++;
                }
                if (colSum !== colCounts[j]) return false;
            }
            return true;
        });
        
        return filteredGrids;
    },
    
    // 获取组合
    getCombinations(arr, k) {
        if (k === 0) return [[]];
        if (k > arr.length) return [];
        
        const result = [];
        const backtrack = (start, current) => {
            if (current.length === k) {
                result.push([...current]);
                return;
            }
            for (let i = start; i < arr.length; i++) {
                current.push(arr[i]);
                backtrack(i + 1, current);
                current.pop();
            }
        };
        backtrack(0, []);
        return result;
    },
    
    // 递归构建网格
    buildGrids(rowIdx, n, m, rowPoss, forcedMust, value, validGrids) {
        if (rowIdx === n) {
            // 构建完整网格
            const grid = Array(n).fill(null).map(() => Array(m).fill(0));
            for (let i = 0; i < n; i++) {
                for (const key of forcedMust) {
                    const [r, c] = key.split(',').map(Number);
                    if (r === i) grid[i][c] = value;
                }
            }
            validGrids.push(grid.map(row => [...row]));
            return;
        }
        
        for (const poss of rowPoss[rowIdx]) {
            const grid = Array(n).fill(null).map(() => Array(m).fill(0));
            
            // 填充强制位置
            for (const key of forcedMust) {
                const [r, c] = key.split(',').map(Number);
                if (r === rowIdx) grid[rowIdx][c] = value;
            }
            
            // 填充当前行的可能位置
            for (const col of poss) {
                grid[rowIdx][col] = value;
            }
            
            // 保存当前行并继续
            const savedRow = [...grid[rowIdx]];
            this.buildGridsWithRow(rowIdx + 1, n, m, rowPoss, forcedMust, value, validGrids, grid);
        }
    },
    
    buildGridsWithRow(rowIdx, n, m, rowPoss, forcedMust, value, validGrids, currentGrid) {
        if (rowIdx === n) {
            validGrids.push(currentGrid.map(row => [...row]));
            return;
        }
        
        for (const poss of rowPoss[rowIdx]) {
            const grid = currentGrid.map(row => [...row]);
            
            // 填充强制位置
            for (const key of forcedMust) {
                const [r, c] = key.split(',').map(Number);
                if (r === rowIdx) grid[rowIdx][c] = value;
            }
            
            // 填充当前行的可能位置
            for (const col of poss) {
                grid[rowIdx][col] = value;
            }
            
            this.buildGridsWithRow(rowIdx + 1, n, m, rowPoss, forcedMust, value, validGrids, grid);
        }
    },
    
    // 找出确定性格子（在所有解中都相同的位置）
    getDeterminedCells(grids, value, n, m) {
        if (grids.length === 0) return new Set();
        
        const determined = new Set();
        for (let i = 0; i < n; i++) {
            for (let j = 0; j < m; j++) {
                const values = new Set(grids.map(g => g[i][j]));
                if (values.size === 1 && values.values().next().value === value) {
                    determined.add(`${i},${j}`);
                }
            }
        }
        return determined;
    },
    
    // 根据约束数字生成约束网格
    generateConstraintGrids() {
        const rows = GameState.rows;
        const cols = GameState.cols;
        const constraints = GameState.constraints;
        const prefilledGrid = this.getPrefilledGrid();
        
        // 生成所有可能的绿色网格
        const greenGrids = this.generatePossibleGrids(
            constraints.left, constraints.top, rows, cols, 1, prefilledGrid
        );
        
        // 生成所有可能的黄色网格
        const yellowGrids = this.generatePossibleGrids(
            constraints.right, constraints.bottom, rows, cols, 2, prefilledGrid
        );
        
        console.log('绿色图可能数量:', greenGrids.length);
        console.log('黄色图可能数量:', yellowGrids.length);
        
        // 找出确定性格子
        const greenDetermined = this.getDeterminedCells(greenGrids, 1, rows, cols);
        const yellowDetermined = this.getDeterminedCells(yellowGrids, 2, rows, cols);
        
        console.log('确定绿的格子:', greenDetermined.size > 0 ? Array.from(greenDetermined) : '无');
        console.log('确定黄的格子:', yellowDetermined.size > 0 ? Array.from(yellowDetermined) : '无');
        
        return {
            greenGrids,
            yellowGrids,
            greenDetermined,
            yellowDetermined
        };
    },
    
    // 获取预填充网格状态
    getPrefilledGrid() {
        return GameState.grid.map(row => [...row]);
    },
    
    // 合并三个网格：约束网格 + 预填充网格
    // 返回：0=空，1=绿，2=黄，3=冲突（红），-1=禁用
    getMergedGrid() {
        const rows = GameState.rows;
        const cols = GameState.cols;
        const result = this.generateConstraintGrids();
        const { greenDetermined, yellowDetermined } = result;
        const prefilledGrid = this.getPrefilledGrid();
        
        const merged = Array(rows).fill(null).map(() => Array(cols).fill(0));
        
        for (let r = 0; r < rows; r++) {
            for (let c = 0; c < cols; c++) {
                const key = `${r},${c}`;
                const isGreenDetermined = greenDetermined.has(key);
                const isYellowDetermined = yellowDetermined.has(key);
                const prefilled = prefilledGrid[r][c];
                
                // 预填充为禁用
                if (prefilled === -1) {
                    merged[r][c] = -1;
                }
                // 预填充为绿色
                else if (prefilled === 1) {
                    merged[r][c] = 1;
                }
                // 预填充为黄色
                else if (prefilled === 2) {
                    merged[r][c] = 2;
                }
                // 预填充为空，根据约束推导
                else {
                    if (isGreenDetermined && isYellowDetermined) {
                        // 冲突（红）
                        merged[r][c] = 3;
                    } else if (isGreenDetermined) {
                        // 确定绿
                        merged[r][c] = 1;
                    } else if (isYellowDetermined) {
                        // 确定黄
                        merged[r][c] = 2;
                    } else {
                        // 空/不确定
                        merged[r][c] = 0;
                    }
                }
            }
        }
        
        // 打印到控制台用于调试
        this.printGridToConsole(merged);
        
        return { merged, conflicts: [] };
    },
    
    // 获取用于求解的绿色约束网格（01 化）
    getGreenConstraintGrid() {
        const rows = GameState.rows;
        const cols = GameState.cols;
        const result = this.generateConstraintGrids();
        const { greenDetermined } = result;
        const prefilledGrid = this.getPrefilledGrid();
        
        const grid = Array(rows).fill(null).map(() => Array(cols).fill(0));
        
        for (let r = 0; r < rows; r++) {
            for (let c = 0; c < cols; c++) {
                const key = `${r},${c}`;
                if (greenDetermined.has(key) || prefilledGrid[r][c] === 1) {
                    if (prefilledGrid[r][c] !== -1) {
                        grid[r][c] = 1;
                    }
                }
            }
        }
        
        return grid;
    },
    
    // 获取用于求解的黄色约束网格（01 化）
    getYellowConstraintGrid() {
        const rows = GameState.rows;
        const cols = GameState.cols;
        const result = this.generateConstraintGrids();
        const { yellowDetermined } = result;
        const prefilledGrid = this.getPrefilledGrid();
        
        const grid = Array(rows).fill(null).map(() => Array(cols).fill(0));
        
        for (let r = 0; r < rows; r++) {
            for (let c = 0; c < cols; c++) {
                const key = `${r},${c}`;
                if (yellowDetermined.has(key) || prefilledGrid[r][c] === 2) {
                    if (prefilledGrid[r][c] !== -1) {
                        grid[r][c] = 1;
                    }
                }
            }
        }
        
        return grid;
    },
    
    // 获取 01 化的约束网格（用于求解）
    getBinaryConstraintGrids() {
        return {
            green: this.getGreenConstraintGrid(),
            yellow: this.getYellowConstraintGrid()
        };
    },
    
    // 检查约束网格与禁用区域和预填充是否冲突
    checkConflicts(greenDetermined, yellowDetermined) {
        const conflicts = [];
        for (const key of greenDetermined) {
            if (yellowDetermined.has(key)) {
                const [r, c] = key.split(',').map(Number);
                conflicts.push(`位置 (${r + 1}, ${c + 1})：既是确定绿又是确定黄`);
            }
        }
        return conflicts;
    },
    
    // 完整的约束验证
    validate() {
        const result = this.generateConstraintGrids();
        const { greenDetermined, yellowDetermined, greenGrids, yellowGrids } = result;
        
        const conflicts = this.checkConflicts(greenDetermined, yellowDetermined);
        
        return {
            valid: conflicts.length === 0 && greenGrids.length > 0 && yellowGrids.length > 0,
            conflicts,
            greenDetermined,
            yellowDetermined,
            greenGrids,
            yellowGrids
        };
    },
    
    // 验证约束是否满足（用于求解后检查）
    checkConstraints(solution) {
        const grid = Array(GameState.rows).fill(null).map(() => Array(GameState.cols).fill(0));
        
        solution.forEach(s => {
            s.cells.forEach(cell => {
                grid[cell.r][cell.c] = cell.color;
            });
        });
        
        // 检查行约束
        for (let r = 0; r < GameState.rows; r++) {
            let greenCount = 0, yellowCount = 0;
            for (let c = 0; c < GameState.cols; c++) {
                if (grid[r][c] === 1) greenCount++;
                if (grid[r][c] === 2) yellowCount++;
            }
            
            if (greenCount !== GameState.constraints.left[r]) return false;
            if (yellowCount !== GameState.constraints.right[r]) return false;
        }
        
        // 检查列约束
        for (let c = 0; c < GameState.cols; c++) {
            let greenCount = 0, yellowCount = 0;
            for (let r = 0; r < GameState.rows; r++) {
                if (grid[r][c] === 1) greenCount++;
                if (grid[r][c] === 2) yellowCount++;
            }
            
            if (greenCount !== GameState.constraints.top[c]) return false;
            if (yellowCount !== GameState.constraints.bottom[c]) return false;
        }
        
        return true;
    },
    
    // 检查放置是否合法
    checkPlacement(shape, startR, startC, existingSolution, availableCellsSet, colorGrid) {
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
                    if (!availableCellsSet.has(cellKey)) {
                        return { valid: false, reason: 'disabled_cell' };
                    }
                    
                    for (const placed of existingSolution) {
                        for (const sc of placed.cells) {
                            if (sc.r === gr && sc.c === gc) {
                                return { valid: false, reason: 'occupied' };
                            }
                        }
                    }
                    
                    if (colorGrid && colorGrid[gr][gc] !== 1) {
                        return { valid: false, reason: 'color_constraint' };
                    }
                    
                    const fixedColor = this.getFixedColor(gr, gc);
                    if (fixedColor !== 0 && fixedColor !== shape[r][c]) {
                        return { valid: false, reason: 'color_mismatch' };
                    }
                    
                    cells.push({ r: gr, c: gc, color: shape[r][c] });
                }
            }
        }
        
        return { valid: true, cells };
    },
    
    getFixedColor(r, c) {
        const cell = GameState.grid[r][c];
        return cell > 0 ? cell : 0;
    },
    
    getAvailableCellsSet() {
        const set = new Set();
        for (let r = 0; r < GameState.rows; r++) {
            for (let c = 0; c < GameState.cols; c++) {
                if (GameState.grid[r][c] !== -1) {
                    set.add(`${r},${c}`);
                }
            }
        }
        return set;
    },
    
    validateBasics() {
        const totalCells = GameState.rows * GameState.cols - 
                          GameState.grid.flat().filter(x => x === -1).length;
        const totalPieces = PieceManager.getTotalCells();
        
        if (totalPieces !== totalCells) {
            return {
                valid: false,
                message: `格子数量不匹配：拼图共${totalPieces}格，可用网格${totalCells}格`
            };
        }
        
        return { valid: true };
    },
    
    // 打印约束网格到控制台
    printGridToConsole(merged) {
        console.log('=== 约束推导网格 ===');
        const labels = ['空', '绿', '黄', '红', '禁'];
        for (let r = 0; r < merged.length; r++) {
            let rowStr = '';
            for (let c = 0; c < merged[r].length; c++) {
                const val = merged[r][c];
                const label = labels[val + 1] || '?';
                rowStr += label + ' ';
            }
            console.log(rowStr);
        }
        console.log('=====================');
    },
    
    // 获取所有可能的组合解
    getAllValidSolutions() {
        const result = this.validate();
        if (!result.valid) return [];
        
        const { greenGrids, yellowGrids } = result;
        const rows = GameState.rows;
        const cols = GameState.cols;
        
        const validSolutions = [];
        
        for (const gGrid of greenGrids) {
            for (const yGrid of yellowGrids) {
                let isValid = true;
                
                // 检查是否有冲突
                for (let r = 0; r < rows && isValid; r++) {
                    for (let c = 0; c < cols && isValid; c++) {
                        // 绿色和黄色不能重叠
                        if (gGrid[r][c] === 1 && yGrid[r][c] === 2) {
                            isValid = false;
                        }
                    }
                }
                
                if (isValid) {
                    // 合并网格
                    const merged = Array(rows).fill(null).map(() => Array(cols).fill(0));
                    for (let r = 0; r < rows; r++) {
                        for (let c = 0; c < cols; c++) {
                            if (gGrid[r][c] === 1) merged[r][c] = 1;
                            else if (yGrid[r][c] === 2) merged[r][c] = 2;
                        }
                    }
                    validSolutions.push(merged);
                }
            }
        }
        
        return validSolutions;
    }
};