export const useToast = () => {
  const toasts = useState('toasts', () => [])

  const addToast = (message, type = 'error') => {
    const id = Date.now()
    toasts.value.push({ id, message, type })
    setTimeout(() => {
      toasts.value = toasts.value.filter(t => t.id !== id)
    }, 4000)
  }

  return { toasts, addToast }
}