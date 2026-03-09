declare module '@toast-ui/editor' {
  interface ToastEditorOptions {
    el: HTMLElement
    height?: string
    initialEditType?: 'markdown' | 'wysiwyg'
    initialValue?: string
    autofocus?: boolean
    usageStatistics?: boolean
    events?: {
      change?: () => void
    }
  }

  export default class Editor {
    constructor(options: ToastEditorOptions)
    getMarkdown(): string
    destroy(): void
  }
}
