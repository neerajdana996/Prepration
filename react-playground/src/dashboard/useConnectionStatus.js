import { useEffect, useState } from 'react'
import { getSocket } from './socket'

// Tracks the shared socket's live/disconnected state for the status indicator.
export function useConnectionStatus() {
  const [status, setStatus] = useState('connecting')

  useEffect(() => {
    const s = getSocket()
    if (s.readyState === WebSocket.OPEN) setStatus('live')

    const onOpen = () => setStatus('live')
    const onClose = () => setStatus('disconnected')
    const onError = () => setStatus('disconnected')

    s.addEventListener('open', onOpen)
    s.addEventListener('close', onClose)
    s.addEventListener('error', onError)
    return () => {
      s.removeEventListener('open', onOpen)
      s.removeEventListener('close', onClose)
      s.removeEventListener('error', onError)
    }
  }, [])

  return status
}
