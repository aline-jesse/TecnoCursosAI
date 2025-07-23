// UndoRedoManager TypeScript module
export interface UndoRedoAction {
  type: string;
  payload?: any;
  timestamp: number;
}

export class UndoRedoManager {
  private history: UndoRedoAction[] = [];
  private currentIndex: number = -1;
  private maxHistory: number = 50;

  public execute(action: UndoRedoAction): void {
    // Remove future history if we're not at the end
    this.history = this.history.slice(0, this.currentIndex + 1);
    
    // Add new action
    this.history.push(action);
    this.currentIndex++;

    // Limit history size
    if (this.history.length > this.maxHistory) {
      this.history.shift();
      this.currentIndex--;
    }
  }

  public canUndo(): boolean {
    return this.currentIndex >= 0;
  }

  public canRedo(): boolean {
    return this.currentIndex < this.history.length - 1;
  }

  public undo(): UndoRedoAction | null {
    if (!this.canUndo()) return null;
    
    const action = this.history[this.currentIndex];
    this.currentIndex--;
    return action;
  }

  public redo(): UndoRedoAction | null {
    if (!this.canRedo()) return null;
    
    this.currentIndex++;
    return this.history[this.currentIndex];
  }

  public clear(): void {
    this.history = [];
    this.currentIndex = -1;
  }

  public getHistory(): UndoRedoAction[] {
    return [...this.history];
  }
}

export default UndoRedoManager;
