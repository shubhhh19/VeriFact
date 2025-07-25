import React, { useState } from 'react'
import NewsValidator from './components/NewsValidator'
import Header from './components/Header'
import Footer from './components/Footer'

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <NewsValidator />
      </main>
      <Footer />
    </div>
  )
}

export default App 