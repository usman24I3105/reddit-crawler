import React, { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext(null)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [workerId, setWorkerId] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('auth_token')
    const storedWorkerId = localStorage.getItem('worker_id')
    
    if (token && storedWorkerId) {
      setIsAuthenticated(true)
      setWorkerId(storedWorkerId)
    }
    setLoading(false)
  }, [])

  const login = (token, workerId) => {
    localStorage.setItem('auth_token', token)
    localStorage.setItem('worker_id', workerId)
    setIsAuthenticated(true)
    setWorkerId(workerId)
  }

  const logout = () => {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('worker_id')
    setIsAuthenticated(false)
    setWorkerId(null)
  }

  const value = {
    isAuthenticated,
    workerId,
    login,
    logout,
    loading,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}





