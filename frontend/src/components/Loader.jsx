import React from 'react'

const Loader = ({ size = 'md' }) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  }

  return (
    <div className="flex justify-center items-center">
      <div
        className={`${sizeClasses[size]} border-4 border-reddit-orange/20 border-t-reddit-orange rounded-full animate-spin`}
      ></div>
    </div>
  )
}

export default Loader
