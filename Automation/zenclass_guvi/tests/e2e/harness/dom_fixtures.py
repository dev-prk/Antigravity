"""
DOM and HTML Fixtures for Guvi CodeKata and ZenClass Platforms.
Reverse-engineered from live production DOM structures and frontend bundles.
"""

# Guvi Sign-In Page HTML fixture
GUVI_LOGIN_HTML = """<!DOCTYPE html>
<html lang="en">
<head><title>Sign In - GUVI</title></head>
<body>
  <div id="login-container">
    <div id="emailgroup">
      <label for="email">Email</label>
      <input type="email" id="email" class="form-control" placeholder="Enter your email">
      <div class="invalid-feedback">Incorrect Email or Password</div>
    </div>
    <div id="passwordGroup">
      <label for="password">Password</label>
      <input type="password" id="password" class="form-control" placeholder="Enter password">
      <div class="invalid-feedback">Incorrect Email or Password</div>
    </div>
    <div class="form-check">
      <input type="checkbox" id="logged-in" class="form-check-input" checked>
      <label for="logged-in">Keep me logged in</label>
    </div>
    <div class="btn-container">
      <a id="login-btn" class="btn login-btn" href="#">Login</a>
      <a id="mobile-login" class="login-btn" href="#">Login</a>
    </div>
    <div id="myModal" class="modal" style="display: none;">
      <div class="modal-content">
        <p>Your account requires activation.</p>
        <button id="sendmail">Resend Activation</button>
      </div>
    </div>
  </div>
</body>
</html>"""

# Guvi CodeKata Table Listing HTML fixture (15 rows, 143 pages simulation)
GUVI_CODEKATA_TABLE_HTML = """<!DOCTYPE html>
<html lang="en" q:render="ssr" q:route="code-kata/">
<head><title>CodeKata - GUVI</title></head>
<body>
  <div class="filter-tabs-container">
    <button class="filter-topics-tab filter-topics-tab-active">Topics</button>
    <button class="filter-topics-tab">Companies</button>
    <button class="filter-topics-tab">Colleges</button>
  </div>
  <table class="table">
    <thead>
      <tr>
        <th>Status</th>
        <th>Problem</th>
        <th>Success Rate</th>
        <th>Difficulty</th>
        <th>Points</th>
      </tr>
    </thead>
    <tbody>
      <tr class="cursor-pointer" data-slug="odd-or-even-sum">
        <td>
          <svg width="20" height="20">
            <g clip-path="url(#completed-icon_svg__a)">
              <path fill="#0DBA4B" d="M10 0C4.48 0 0 4.48 0 10s4.48 10 10 10 10-4.48 10-10S15.52 0 10 0zm-2 15l-5-5 1.41-1.41L8 12.17l7.59-7.59L17 6l-9 9z"/>
            </g>
          </svg>
        </td>
        <td class="problem-title">1. Odd or Even Sum</td>
        <td class="success-rate">73.97%</td>
        <td class="difficulty">Easy</td>
        <td class="points">30</td>
      </tr>
      <tr class="cursor-pointer" data-slug="reverse-a-string">
        <td>
          <svg width="20" height="20"><g></g></svg>
        </td>
        <td class="problem-title">2. Reverse a String</td>
        <td class="success-rate">68.20%</td>
        <td class="difficulty">Easy</td>
        <td class="points">30</td>
      </tr>
      <tr class="cursor-pointer" data-slug="sum-of-array">
        <td>
          <svg width="20" height="20"><g></g></svg>
        </td>
        <td class="problem-title">3. Sum of Array Elements</td>
        <td class="success-rate">81.12%</td>
        <td class="difficulty">Easy</td>
        <td class="points">20</td>
      </tr>
      <tr class="cursor-pointer" data-slug="palindrome-check">
        <td>
          <svg width="20" height="20"><g></g></svg>
        </td>
        <td class="problem-title">4. Palindrome Checker</td>
        <td class="success-rate">55.40%</td>
        <td class="difficulty">Medium</td>
        <td class="points">40</td>
      </tr>
      <tr class="cursor-pointer" data-slug="prime-numbers-count">
        <td>
          <svg width="20" height="20">
            <g clip-path="url(#completed-icon_svg__a)">
              <path fill="#0DBA4B" d="M10 0C4.48 0 0 4.48 0 10s4.48 10 10 10 10-4.48 10-10S15.52 0 10 0zm-2 15l-5-5 1.41-1.41L8 12.17l7.59-7.59L17 6l-9 9z"/>
            </g>
          </svg>
        </td>
        <td class="problem-title">5. Count Prime Numbers</td>
        <td class="success-rate">42.80%</td>
        <td class="difficulty">Hard</td>
        <td class="points">50</td>
      </tr>
    </tbody>
  </table>
  <div class="pagination-wrapper">
    <button class="prev-page" disabled>Go to previous page</button>
    <button class="page-pill active">1</button>
    <button class="page-pill">2</button>
    <button class="page-pill">3</button>
    <button class="page-pill">143</button>
    <button class="next-page">Go to next page</button>
  </div>
</body>
</html>"""

# Guvi Problem Workspace HTML fixture (Ace Editor + Run + Submit + Modals)
GUVI_WORKSPACE_HTML = """<!DOCTYPE html>
<html lang="en">
<head><title>Odd or Even Sum - CodeKata - GUVI</title></head>
<body>
  <div class="workspace-container">
    <div class="problem-details-pane">
      <h1 class="problem-title">Odd or Even Sum</h1>
      <span class="question-status">Unsolved</span>
      <div class="problem-statement">
        Given two numbers N and M, add them and state whether the sum is even or odd.
      </div>
      <div class="input-description">
        Two integers N and M separated by space.
      </div>
      <div class="output-description">
        Print "even" or "odd" without quotes.
      </div>
      <div class="sample-input">
        9 2
      </div>
      <div class="sample-output">
        odd
      </div>
    </div>
    <div class="editor-pane">
      <select id="editorModeSelectDesktop">
        <option value="PYTHON 3" selected>PYTHON 3</option>
        <option value="JAVASCRIPT">JAVASCRIPT</option>
      </select>
      <div id="editor" class="ace_editor">
        <textarea class="ace_text-input" spellcheck="false"></textarea>
        <div class="ace_scroller">
          <div class="ace_content">
            <div class="ace_layer ace_text-layer">
              <div class="ace_line"># Starter Code</div>
            </div>
          </div>
        </div>
      </div>
      <div class="action-buttons">
        <button class="run-code rounded-lg text-white">Run Code</button>
        <button class="submit-code rounded-lg text-white">Submit Code</button>
      </div>
      <div class="test-results-pane" style="display: none;">
        <button class="active-test-pill">Test Case 1</button>
        <button class="inactive-test-pill">Test Case 2</button>
        <div class="test-pill-status">Correct Answer</div>
      </div>
    </div>
    <div id="progress_modal" style="display: none;">Testing 100%...</div>
    <div id="success_modal" class="modal" style="display: none;">
      <div class="modal-content">
        <h2>Congratulations! You have earned +30 Geekoins</h2>
        <span class="earned-points">+30 Geekoins</span>
      </div>
    </div>
  </div>
</body>
</html>"""

# ZenClass Sign-In HTML fixture
ZENCLASS_LOGIN_HTML = """<!DOCTYPE html>
<html lang="en">
<head><title>Zen Class Login</title></head>
<body>
  <div id="root">
    <div class="login-content-wrapper">
      <div class="email-input">
        <input type="text" placeholder="Enter your mail" value="">
      </div>
      <div class="password-input">
        <input type="password" placeholder="Enter your password " value="">
        <button aria-label="toggle password visibility">Show</button>
      </div>
      <div class="radio-input-container">
        <input type="checkbox" id="remember-me">
        <label for="remember-me">Remember Me</label>
      </div>
      <div class="sign-in-btn-container">
        <button class="primary-btn sign-in-pad">Sign in</button>
      </div>
      <div class="validation-error" style="display: none;"></div>
    </div>
  </div>
</body>
</html>"""

# ZenClass Tasks Kanban Board HTML fixture
ZENCLASS_TASKS_HTML = """<!DOCTYPE html>
<html lang="en">
<head><title>Zen Class Tasks</title></head>
<body>
  <div id="root">
    <div class="row commonTaskContainer">
      <div class="column active-tasks">
        <h2 class="active-tasks-heading">Active Tasks (<span class="active-tasks-count">2</span>)</h2>
        <div class="itemactive-tasks" id="individual-card" data-task-id="task-101">
          <div class="Task-name-and-mark">
            <span class="task-name">Day 1: Basic JavaScript Functions</span>
          </div>
          <div class="language-tag-container">
            <span class="common-tags">JavaScript</span>
          </div>
          <div class="view-task-container">
            <button class="view-btn">View Task</button>
          </div>
          <div class="action-container">
            <button class="primary-outlined-submit-btn">Submit</button>
          </div>
        </div>
      </div>
      <div class="column pending-tasks">
        <h2 class="pending-tasks-heading">Pending Tasks (<span class="pending-tasks-count">1</span>)</h2>
        <div class="itempending-tasks" id="individual-card" data-task-id="task-102">
          <div class="Task-name-and-mark">
            <span class="task-name">Day 2: Async Await & Fetch API</span>
            <span class="redo-label-container"><span class="redo-text">Redo</span></span>
          </div>
          <div class="language-tag-container">
            <span class="common-tags">JavaScript</span>
          </div>
          <div class="action-container">
            <button class="primary-outlined-submit-btn">Re-submit</button>
          </div>
        </div>
      </div>
      <div class="column completed-tasks">
        <h2 class="completed-tasks-heading">Completed Tasks (<span class="completed-tasks-count">1</span>)</h2>
        <div class="itemcompleted-tasks" id="individual-card" data-task-id="task-100">
          <div class="Task-name-and-mark">
            <span class="task-name">Day 0: HTML & CSS Introduction</span>
          </div>
          <div class="score-container">
            <span class="common-score-text">10/10</span>
          </div>
          <div class="action-container">
            <button class="student-task-btn student-task-edit-btn">Edit</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</body>
</html>"""

# ZenClass Dynamic Submission Modal HTML fixture (Module 41486)
ZENCLASS_SUBMISSION_MODAL_HTML = """<div class="submit-form-container-web">
  <h3>Submit Task</h3>
  <div class="submit-form-title-textField-wrapper" data-field-key="frontEnd_Deployed_Url">
    <label class="form-label-text">Frontend Deployed URL</label>
    <input type="text" placeholder="Enter Link" class="url-input" value="">
    <span class="validation-error-text" style="display:none;"></span>
  </div>
  <div class="submit-form-title-textField-wrapper" data-field-key="frontEnd_SourceCode">
    <label class="form-label-text">Frontend Source code</label>
    <input type="text" placeholder="Enter Link" class="url-input" value="">
    <span class="validation-error-text" style="display:none;"></span>
  </div>
  <div class="submit-form-title-textField-wrapper" data-field-key="github_Url">
    <label class="form-label-text">Github URL</label>
    <input type="text" placeholder="Enter Link" class="url-input" value="">
    <span class="validation-error-text" style="display:none;"></span>
  </div>
  <div class="form-submit-container">
    <button class="primary-btn submit-modal-btn">Submit</button>
  </div>
  <div id="feedback-modal" class="confirmation-modal" style="display: none;">
    <p class="modal-message">Task Submitted Suceessfully</p>
  </div>
</div>"""

# ZenClass Projects Kanban HTML fixture
ZENCLASS_PROJECTS_HTML = """<!DOCTYPE html>
<html lang="en">
<head><title>Zen Class Projects</title></head>
<body>
  <div id="root">
    <div class="projectCardcontainer-main">
      <div class="commonTaskContainer">
        <div class="column active-projects">
          <h2 class="active-Project-heading">Active Projects (<span class="active-Project-count">1</span>)</h2>
          <div class="itemactive-Project" id="individual-card" data-project-id="proj-501">
            <div class="Project-name-and-mark">
              <span class="project-name">Full Stack E-Commerce Platform</span>
            </div>
            <div class="language-tag-container">
              <span class="common-tags">React</span>
              <span class="common-tags">Node.js</span>
            </div>
            <div class="project-actions">
              <button class="primary-outlined-submit-btn">Submit</button>
            </div>
          </div>
        </div>
        <div class="column pending-projects">
          <h2 class="pending-Project-heading">Pending Projects (<span class="pending-Project-count">0</span>)</h2>
        </div>
        <div class="column completed-projects">
          <h2 class="completed-Project-heading">Completed Projects (<span class="completed-Project-count">1</span>)</h2>
          <div class="itemcompleted-Project" id="individual-card" data-project-id="proj-500">
            <div class="Project-name-and-mark">
              <span class="project-name">Portfolio Website</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</body>
</html>"""
