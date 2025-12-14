# Instructor Panel - High-Level Project Plan

## 📋 Project Overview

**Goal**: Build an instructor dashboard where teachers can create and manage course content using a markdown editor, separate from the admin panel.

**Current State**: 
- ✅ Database models support instructors (`is_instructor` flag in TutorialUser)
- ✅ Admin panel exists for platform management
- ✅ Course relationships properly defined (instructor_id in NewTutorial)
- ❌ No instructor-specific interface
- ❌ No markdown editor for content creation

---

## 🎯 Core Requirements

### 1. User Roles
- **Instructor**: Can create/edit their own courses only
- **Admin**: Can manage all courses + platform settings (existing)
- **Student**: Can enroll and learn (existing)

### 2. Key Features
- Markdown-based course content editor
- Course management (CRUD for own courses)
- Lesson and exercise creation
- Content preview before publishing
- Basic analytics for instructor's courses

---

## 🏗️ High-Level Architecture

```
/instructor                  → Instructor dashboard (course list, stats)
/instructor/courses/create   → Create new course
/instructor/courses/{id}/edit → Edit course metadata
/instructor/courses/{id}/lessons/create → Create lesson with markdown editor
/instructor/courses/{id}/lessons/{id}/edit → Edit lesson
/instructor/courses/{id}/exercises/create → Create exercise
/instructor/courses/{id}/preview → Preview course before publishing
```

### Technical Components
1. **Flask Blueprint**: `app/instructor/` (new)
2. **Decorator**: `@instructor_required` (check `current_user.is_instructor`)
3. **Templates**: `app/templates/instructor/` (new)
4. **Forms**: Course, Lesson, Exercise forms (similar to admin but scoped)
5. **Frontend**: Markdown editor library (e.g., SimpleMDE, EasyMDE)

---

## 📦 Implementation Phases

### **Phase 1: Foundation** (Week 1)
- [ ] Create `app/instructor/` blueprint with routes
- [ ] Add `@instructor_required` decorator
- [ ] Create instructor dashboard page (list own courses)
- [ ] Add "Become an Instructor" flow (request → admin approval)

**Deliverables**: Working instructor dashboard showing logged-in instructor's courses

---

### **Phase 2: Course Management** (Week 2)
- [ ] Create/Edit course functionality (metadata only)
- [ ] Course list with status (draft/published)
- [ ] Publish/unpublish course action
- [ ] Delete own course (soft delete)

**Deliverables**: Instructors can create course shells with metadata

---

### **Phase 3: Markdown Editor Integration** (Week 3)
- [ ] Integrate markdown editor library (SimpleMDE or EasyMDE)
- [ ] Create lesson with markdown content
- [ ] Edit lesson with live preview
- [ ] Save as draft or publish
- [ ] Image upload for lesson content

**Deliverables**: Instructors can write lessons in markdown with live preview

---

### **Phase 4: Exercises & Quizzes** (Week 4)
- [ ] Create coding exercises (Python/SQL)
- [ ] Add test cases for exercises
- [ ] Create multiple-choice quizzes
- [ ] Link exercises to lessons

**Deliverables**: Complete course creation capability

---

### **Phase 5: Polish & Analytics** (Week 5)
- [ ] Course preview mode (before publishing)
- [ ] Basic instructor analytics (enrollment count, completion rate)
- [ ] Drag-and-drop lesson reordering
- [ ] Course templates (starter markdown for common course types)

**Deliverables**: Production-ready instructor panel

---

## 🔒 Access Control Logic

```python
# Simplified authorization rules

def can_edit_course(user, course):
    """Check if user can edit course"""
    if user.is_admin:
        return True  # Admins can edit any course
    if user.is_instructor and course.instructor_id == user.id:
        return True  # Instructors can edit their own courses
    return False

# Applied in routes:
@instructor_bp.route('/courses/<int:course_id>/edit')
@login_required
@instructor_required
def edit_course(course_id):
    course = NewTutorial.query.get_or_404(course_id)
    if not can_edit_course(current_user, course):
        abort(403)
    # ... rest of route logic
```

---

## 📊 Database Changes Needed

**None!** Existing schema already supports instructors:
- ✅ `TutorialUser.is_instructor` - flag existing
- ✅ `NewTutorial.instructor_id` - relationship existing
- ✅ All content tables (Lesson, Exercise, Quiz) already exist

**Optional enhancements** (future):
- Add `instructor_profile` table for bio, expertise, social links
- Add `course_revenue_share` table for payout tracking

---

## 🎨 UI/UX Flow

### Instructor Journey
1. **Login** → Redirected to `/instructor/dashboard`
2. **Dashboard** → See list of own courses + quick stats
3. **Create Course** → Fill metadata form (title, description, price)
4. **Add Lessons** → Click "Add Lesson" → Open markdown editor
5. **Write Content** → Type markdown in left panel, see preview on right
6. **Add Exercises** → Create coding challenges with test cases
7. **Preview** → View course as student would see it
8. **Publish** → Make course available to students

### Admin Journey (unchanged)
- Admin continues using `/admin` panel
- Admin can approve instructor requests
- Admin can edit any course if needed

---

## 🛠️ Technology Stack

### Backend
- Flask blueprints (new `instructor` blueprint)
- Existing models (no changes needed)
- WTForms for form validation
- Markdown rendering: `markdown2` or `mistune` library

### Frontend
- **Markdown Editor**: [EasyMDE](https://github.com/Ionaru/easy-markdown-editor) (lightweight, MIT license)
- **Syntax Highlighting**: Prism.js or Highlight.js
- **Image Upload**: Flask file upload + storage (local or S3)
- **Styling**: Bootstrap (keep consistent with existing admin panel)

---

## 🚀 Quick Start (Phase 1)

### Minimal Viable Product (MVP)
**Goal**: Instructor can log in, see their courses, and create a basic course

**3-File Implementation**:
1. `app/instructor/__init__.py` - Blueprint registration
2. `app/instructor/routes.py` - Dashboard and course CRUD routes
3. `app/templates/instructor/dashboard.html` - Simple course list page

**Time estimate**: 2-3 days for functional MVP

---

## 📝 Content Creation Workflow (Final)

```
Instructor writes markdown:
┌─────────────────────┬──────────────────────┐
│ # Python Basics     │ Python Basics        │
│                     │                      │
│ Variables store...  │ Variables store...   │
│                     │                      │
│ ```python           │ print("Hello!")      │
│ print("Hello!")     │ [syntax highlighted] │
│ ```                 │                      │
│                     │                      │
│ ![diagram](img.png) │ [Image renders]      │
│                     │                      │
│ [Save Draft]        │ [Publish Lesson]     │
└─────────────────────┴──────────────────────┘
```

**Markdown → HTML Pipeline**:
1. Instructor writes markdown
2. Server converts markdown to HTML (using `markdown2`)
3. Store HTML in `Lesson.content` field
4. Display rendered HTML to students

---

## ⚠️ Key Decisions

### Decision 1: Markdown Storage
**Option A**: Store markdown source + generate HTML on-the-fly
**Option B**: Store HTML only (convert once on save)
**Recommendation**: Store markdown in database, convert to HTML on save, cache rendered HTML

### Decision 2: Image Handling
**Option A**: Upload to local `/static/uploads/` folder
**Option B**: Upload to S3/CDN
**Recommendation**: Start with local storage, migrate to S3 later

### Decision 3: Editor Library
**Option A**: SimpleMDE (older, widely used)
**Option B**: EasyMDE (modern fork of SimpleMDE)
**Option C**: Toast UI Editor (feature-rich but heavier)
**Recommendation**: EasyMDE for balance of features and simplicity

---

## 🎯 Success Metrics

### Phase 1 Complete When:
- Instructor can log in and see dashboard
- Instructor sees only their own courses
- Basic navigation works

### Project Complete When:
- Instructor can create full course (metadata + lessons + exercises)
- Markdown editor works with live preview
- Course can be published and viewed by students
- Basic analytics visible (enrollment count)

---

## 🔄 Differences: Admin vs Instructor Panel

| Feature | Admin Panel | Instructor Panel |
|---------|-------------|------------------|
| **URL** | `/admin` | `/instructor` |
| **Access** | Admins only | Instructors + Admins |
| **View Courses** | All courses | Own courses only |
| **Edit Courses** | Any course | Own courses only |
| **User Management** | Yes | No |
| **Platform Settings** | Yes | No |
| **Analytics** | Platform-wide | Own courses only |
| **Revenue** | Total platform | Own earnings only |

---

## 📅 Timeline Summary

- **Week 1**: Instructor blueprint + dashboard
- **Week 2**: Course CRUD (metadata)
- **Week 3**: Markdown editor integration
- **Week 4**: Exercises and quizzes
- **Week 5**: Polish and analytics

**Total**: ~5 weeks to production-ready instructor panel

---

## 🎓 Next Steps

1. **Review this plan** with team
2. **Set up development environment** (ensure `markdown2` installed)
3. **Create Git branch**: `feature/instructor-panel`
4. **Start Phase 1**: Create blueprint and basic dashboard
5. **Iterate**: Get instructor feedback after each phase

---

## 📚 References

- **Models**: Already defined in `app/models.py`
- **Admin Panel**: Reference `app/admin/` for similar patterns
- **EasyMDE Docs**: https://github.com/Ionaru/easy-markdown-editor
- **Markdown Library**: https://github.com/trentm/python-markdown2

---

**End of Plan** ✅
