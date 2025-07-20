import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Components
const TravelApp = () => {
  const [travelLists, setTravelLists] = useState([]);
  const [currentList, setCurrentList] = useState(null);
  const [categories, setCategories] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showAddItemForm, setShowAddItemForm] = useState(false);

  // Load data on component mount
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const [categoriesRes, listsRes] = await Promise.all([
        axios.get(`${API}/categories`),
        axios.get(`${API}/travel-lists`)
      ]);
      
      setCategories(categoriesRes.data);
      setTravelLists(listsRes.data);
      
      if (listsRes.data.length > 0) {
        setCurrentList(listsRes.data[0]);
        await loadStats(listsRes.data[0].id);
      }
    } catch (error) {
      console.error("Error loading data:", error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async (listId) => {
    try {
      const response = await axios.get(`${API}/travel-lists/${listId}/stats`);
      setStats(response.data);
    } catch (error) {
      console.error("Error loading stats:", error);
    }
  };

  const createTravelList = async (name, destination) => {
    try {
      const response = await axios.post(`${API}/travel-lists`, { name, destination });
      const newList = response.data;
      setTravelLists([...travelLists, newList]);
      setCurrentList(newList);
      await loadStats(newList.id);
      setShowCreateForm(false);
    } catch (error) {
      console.error("Error creating travel list:", error);
    }
  };

  const toggleItemPacked = async (itemId, isPacked) => {
    try {
      await axios.put(`${API}/travel-lists/${currentList.id}/items/${itemId}`, {
        is_packed: !isPacked
      });
      
      // Update local state
      const updatedItems = currentList.items.map(item =>
        item.id === itemId ? { ...item, is_packed: !isPacked } : item
      );
      setCurrentList({ ...currentList, items: updatedItems });
      await loadStats(currentList.id);
    } catch (error) {
      console.error("Error updating item:", error);
    }
  };

  const updateItemNotes = async (itemId, notes) => {
    try {
      await axios.put(`${API}/travel-lists/${currentList.id}/items/${itemId}`, { notes });
      
      // Update local state
      const updatedItems = currentList.items.map(item =>
        item.id === itemId ? { ...item, notes } : item
      );
      setCurrentList({ ...currentList, items: updatedItems });
    } catch (error) {
      console.error("Error updating notes:", error);
    }
  };

  const addCustomItem = async (itemData) => {
    try {
      const response = await axios.post(`${API}/travel-lists/${currentList.id}/items`, itemData);
      const newItem = response.data;
      
      setCurrentList({
        ...currentList,
        items: [...currentList.items, newItem]
      });
      await loadStats(currentList.id);
      setShowAddItemForm(false);
    } catch (error) {
      console.error("Error adding item:", error);
    }
  };

  const deleteItem = async (itemId) => {
    try {
      await axios.delete(`${API}/travel-lists/${currentList.id}/items/${itemId}`);
      
      const updatedItems = currentList.items.filter(item => item.id !== itemId);
      setCurrentList({ ...currentList, items: updatedItems });
      await loadStats(currentList.id);
    } catch (error) {
      console.error("Error deleting item:", error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-purple-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 text-lg">جاري تحميل قائمة السفر...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50" dir="rtl">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">📋 قائمة مستلزمات السفر</h1>
          <p className="text-gray-600">نظم رحلتك بسهولة وتأكد من عدم نسيان أي شيء مهم</p>
        </header>

        {/* Main Content */}
        {!currentList ? (
          <WelcomeScreen onCreateList={() => setShowCreateForm(true)} />
        ) : (
          <>
            {/* Stats Cards */}
            {stats && <StatsCards stats={stats} />}
            
            {/* Travel List Header */}
            <div className="bg-white rounded-2xl shadow-lg p-6 mb-8">
              <div className="flex justify-between items-center mb-4">
                <div>
                  <h2 className="text-2xl font-bold text-gray-800">{currentList.name}</h2>
                  {currentList.destination && (
                    <p className="text-gray-600">🌍 {currentList.destination}</p>
                  )}
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => setShowAddItemForm(true)}
                    className="px-4 py-2 bg-green-500 text-white rounded-xl hover:bg-green-600 transition-colors"
                  >
                    ➕ إضافة عنصر
                  </button>
                  <button
                    onClick={() => setShowCreateForm(true)}
                    className="px-4 py-2 bg-purple-500 text-white rounded-xl hover:bg-purple-600 transition-colors"
                  >
                    ✨ قائمة جديدة
                  </button>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-gradient-to-r from-green-400 to-green-600 h-3 rounded-full transition-all duration-500"
                  style={{ width: `${stats?.progress_percentage || 0}%` }}
                ></div>
              </div>
              <p className="text-sm text-gray-600 mt-2">
                {stats?.progress_percentage || 0}% مكتمل ({stats?.packed_items || 0} من {stats?.total_items || 0})
              </p>
            </div>

            {/* Items by Category */}
            <ItemsByCategory
              categories={categories}
              items={currentList.items}
              onToggleItem={toggleItemPacked}
              onUpdateNotes={updateItemNotes}
              onDeleteItem={deleteItem}
            />
          </>
        )}

        {/* Modals */}
        {showCreateForm && (
          <CreateListModal
            onClose={() => setShowCreateForm(false)}
            onSubmit={createTravelList}
          />
        )}

        {showAddItemForm && (
          <AddItemModal
            categories={categories}
            onClose={() => setShowAddItemForm(false)}
            onSubmit={addCustomItem}
          />
        )}
      </div>
    </div>
  );
};

// Welcome Screen Component
const WelcomeScreen = ({ onCreateList }) => (
  <div className="text-center py-16">
    <div className="bg-white rounded-2xl shadow-lg p-12 max-w-2xl mx-auto">
      <div className="text-6xl mb-6">✈️</div>
      <h2 className="text-3xl font-bold text-gray-800 mb-4">مرحباً بك في قائمة مستلزمات السفر!</h2>
      <p className="text-gray-600 mb-8 text-lg">
        ابدأ بإنشاء قائمة جديدة لرحلتك وتأكد من عدم نسيان أي شيء مهم
      </p>
      <button
        onClick={onCreateList}
        className="px-8 py-3 bg-purple-500 text-white text-xl rounded-xl hover:bg-purple-600 transition-colors transform hover:scale-105"
      >
        🎒 إنشاء قائمة جديدة
      </button>
    </div>
  </div>
);

// Stats Cards Component
const StatsCards = ({ stats }) => (
  <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
    <div className="stats-card stats-card-total">
      <div className="stats-icon">📦</div>
      <div className="stats-content">
        <div className="stats-number">{stats.total_items}</div>
        <div className="stats-label">إجمالي العناصر</div>
      </div>
    </div>
    <div className="stats-card stats-card-completed">
      <div className="stats-icon">✅</div>
      <div className="stats-content">
        <div className="stats-number">{stats.packed_items}</div>
        <div className="stats-label">تم تحضيرها</div>
      </div>
    </div>
    <div className="stats-card stats-card-remaining">
      <div className="stats-icon">⏳</div>
      <div className="stats-content">
        <div className="stats-number">{stats.remaining_items}</div>
        <div className="stats-label">متبقية</div>
      </div>
    </div>
    <div className="stats-card stats-card-progress">
      <div className="stats-icon">📊</div>
      <div className="stats-content">
        <div className="stats-number">{stats.progress_percentage}%</div>
        <div className="stats-label">نسبة الإنجاز</div>
      </div>
    </div>
  </div>
);

// Items by Category Component
const ItemsByCategory = ({ categories, items, onToggleItem, onUpdateNotes, onDeleteItem }) => {
  const groupedItems = items.reduce((groups, item) => {
    const category = item.category || 'miscellaneous';
    if (!groups[category]) groups[category] = [];
    groups[category].push(item);
    return groups;
  }, {});

  return (
    <div className="space-y-8">
      {categories.map(category => {
        const categoryItems = groupedItems[category.id] || [];
        if (categoryItems.length === 0) return null;

        return (
          <div key={category.id} className="bg-white rounded-2xl shadow-lg overflow-hidden">
            <div className={`px-6 py-4 ${category.color} border-b`}>
              <div className="flex items-center">
                <span className="text-2xl ml-3">{category.icon}</span>
                <h3 className="text-xl font-bold">{category.name_ar}</h3>
                <span className="mr-auto bg-white px-3 py-1 rounded-full text-sm font-medium">
                  {categoryItems.filter(item => item.is_packed).length} / {categoryItems.length}
                </span>
              </div>
            </div>
            
            <div className="p-6">
              <div className="space-y-4">
                {categoryItems.map(item => (
                  <TravelItem
                    key={item.id}
                    item={item}
                    onToggle={onToggleItem}
                    onUpdateNotes={onUpdateNotes}
                    onDelete={onDeleteItem}
                  />
                ))}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

// Travel Item Component
const TravelItem = ({ item, onToggle, onUpdateNotes, onDelete }) => {
  const [isEditingNotes, setIsEditingNotes] = useState(false);
  const [notes, setNotes] = useState(item.notes || '');

  const handleNotesSubmit = () => {
    onUpdateNotes(item.id, notes);
    setIsEditingNotes(false);
  };

  return (
    <div className={`p-4 rounded-xl border-2 transition-all duration-300 ${
      item.is_packed 
        ? 'bg-green-50 border-green-200' 
        : 'bg-gray-50 border-gray-200 hover:border-purple-200'
    }`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center flex-1">
          <button
            onClick={() => onToggle(item.id, item.is_packed)}
            className={`w-6 h-6 rounded-full border-2 ml-3 flex items-center justify-center transition-all ${
              item.is_packed
                ? 'bg-green-500 border-green-500 text-white'
                : 'border-gray-300 hover:border-green-500'
            }`}
          >
            {item.is_packed && '✓'}
          </button>
          
          <div className="flex-1">
            <span className={`text-lg ${item.is_packed ? 'line-through text-gray-500' : 'text-gray-800'}`}>
              {item.name_ar}
            </span>
            {item.notes && !isEditingNotes && (
              <p className="text-sm text-gray-600 mt-1">📝 {item.notes}</p>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsEditingNotes(!isEditingNotes)}
            className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
            title="إضافة ملاحظة"
          >
            📝
          </button>
          <button
            onClick={() => onDelete(item.id)}
            className="p-2 text-gray-400 hover:text-red-600 transition-colors"
            title="حذف العنصر"
          >
            🗑️
          </button>
        </div>
      </div>

      {isEditingNotes && (
        <div className="mt-3 pt-3 border-t border-gray-200">
          <div className="flex gap-2">
            <input
              type="text"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="أضف ملاحظة..."
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500"
            />
            <button
              onClick={handleNotesSubmit}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              حفظ
            </button>
            <button
              onClick={() => setIsEditingNotes(false)}
              className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
            >
              إلغاء
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

// Create List Modal Component
const CreateListModal = ({ onClose, onSubmit }) => {
  const [name, setName] = useState('');
  const [destination, setDestination] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (name.trim()) {
      onSubmit(name.trim(), destination.trim());
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-white rounded-2xl p-8 max-w-md w-full mx-4" onClick={(e) => e.stopPropagation()}>
        <h3 className="text-2xl font-bold text-gray-800 mb-6">إنشاء قائمة سفر جديدة</h3>
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2">
              اسم القائمة *
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:border-purple-500"
              placeholder="مثال: رحلة دبي 2024"
              required
            />
          </div>
          
          <div className="mb-6">
            <label className="block text-gray-700 text-sm font-bold mb-2">
              الوجهة (اختياري)
            </label>
            <input
              type="text"
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:border-purple-500"
              placeholder="مثال: دبي، الإمارات العربية المتحدة"
            />
          </div>
          
          <div className="flex gap-3">
            <button
              type="submit"
              className="flex-1 px-6 py-3 bg-purple-500 text-white rounded-xl hover:bg-purple-600 transition-colors"
            >
              إنشاء القائمة
            </button>
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-3 bg-gray-500 text-white rounded-xl hover:bg-gray-600 transition-colors"
            >
              إلغاء
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Add Item Modal Component  
const AddItemModal = ({ categories, onClose, onSubmit }) => {
  const [name, setName] = useState('');
  const [nameAr, setNameAr] = useState('');
  const [category, setCategory] = useState('miscellaneous');
  const [notes, setNotes] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (name.trim() && nameAr.trim()) {
      onSubmit({
        name: name.trim(),
        name_ar: nameAr.trim(),
        category,
        notes: notes.trim()
      });
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-white rounded-2xl p-8 max-w-md w-full mx-4" onClick={(e) => e.stopPropagation()}>
        <h3 className="text-2xl font-bold text-gray-800 mb-6">إضافة عنصر جديد</h3>
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2">
              الاسم بالعربية *
            </label>
            <input
              type="text"
              value={nameAr}
              onChange={(e) => setNameAr(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:border-purple-500"
              placeholder="مثال: كاميرا رقمية"
              required
            />
          </div>

          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2">
              الاسم بالإنجليزية *
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:border-purple-500"
              placeholder="Example: Digital Camera"
              required
            />
          </div>
          
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2">
              الفئة
            </label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:border-purple-500"
            >
              {categories.map(cat => (
                <option key={cat.id} value={cat.id}>
                  {cat.icon} {cat.name_ar}
                </option>
              ))}
            </select>
          </div>
          
          <div className="mb-6">
            <label className="block text-gray-700 text-sm font-bold mb-2">
              ملاحظات (اختياري)
            </label>
            <input
              type="text"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:border-purple-500"
              placeholder="أي ملاحظات إضافية..."
            />
          </div>
          
          <div className="flex gap-3">
            <button
              type="submit"
              className="flex-1 px-6 py-3 bg-green-500 text-white rounded-xl hover:bg-green-600 transition-colors"
            >
              إضافة العنصر
            </button>
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-3 bg-gray-500 text-white rounded-xl hover:bg-gray-600 transition-colors"
            >
              إلغاء
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <TravelApp />
    </div>
  );
}

export default App;