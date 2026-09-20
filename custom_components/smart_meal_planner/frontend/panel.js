/*
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lennox Matzerath (GamingonTour1)
*/

class SmartMealPlannerPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._hass = null;
    this._lastKey = '';
    this._modalRecipe = null;
  }

  set hass(value) {
    this._hass = value;
    const entity = this._findEntity();
    const key = entity ? `${entity.last_updated}-${JSON.stringify(entity.attributes.week || {})}` : 'none';
    if (key !== this._lastKey) {
      this._lastKey = key;
      this.render();
    }
  }

  set narrow(_) {}
  set panel(value) { this._panel = value; }

  connectedCallback() { this.render(); }

  _findEntity() {
    if (!this._hass) return null;
    return Object.values(this._hass.states).find(
      e => e.attributes?.integration === 'smart_meal_planner' && Array.isArray(e.attributes?.week?.days)
    );
  }

  _week() {
    return this._findEntity()?.attributes?.week || {days: []};
  }

  async _call(service, data = {}) {
    await this._hass.callService('smart_meal_planner', service, data);
  }

  _esc(value) {
    return String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  }

  _fmtDate(raw) {
    try {
      return new Intl.DateTimeFormat('de-DE', {day:'2-digit', month:'2-digit'}).format(new Date(`${raw}T12:00:00`));
    } catch (_) {
      return raw;
    }
  }

  _tagName(tag) {
    return ({fish:'Fisch', vegetarian:'Vegetarisch', meat:'Fleisch', pasta:'Nudeln', rice:'Reis', potatoes:'Kartoffeln'})[tag] || tag;
  }

  _recipeMeta(recipe) {
    const values = [];
    if (recipe.minutes) values.push(`${recipe.minutes} Min.`);
    if (recipe.servings) values.push(typeof recipe.servings === 'number' ? `${recipe.servings} Portionen` : this._esc(recipe.servings));
    if (recipe.source) values.push(this._esc(recipe.source));
    return values.join(' · ');
  }

  render() {
    if (!this.shadowRoot) return;
    const entity = this._findEntity();
    if (!entity) {
      this.shadowRoot.innerHTML = `${this._style()}<div class="page"><div class="empty"><h2>Smart Meal Planner</h2><p>Die Integration wird geladen oder ist noch nicht eingerichtet.</p></div></div>`;
      return;
    }

    const attrs = entity.attributes;
    const week = attrs.week;
    const days = week.days || [];
    const planned = days.filter(day => day.selected).length;
    const start = days[0]?.date || '';
    const end = days[6]?.date || '';

    this.shadowRoot.innerHTML = `${this._style()}
      <div class="page">
        <header>
          <div>
            <div class="eyebrow">SMART MEAL PLANNER</div>
            <h1>Essensplan</h1>
            <p>${this._fmtDate(start)} – ${this._fmtDate(end)} · ${planned}/7 Tage geplant</p>
          </div>
          <div class="actions">
            <button class="secondary" data-action="import">＋ Rezept importieren</button>
            ${attrs.internet_enabled ? '<button class="secondary" data-action="sync">☁ Online-Katalog</button>' : ''}
            <button class="secondary" data-action="settings">⚙ Einstellungen</button>
            <button class="primary" data-action="generate-week">↻ Woche vorschlagen</button>
          </div>
        </header>

        <div class="stats">
          <div><b>${attrs.recipe_count ?? 0}</b><span>Rezepte insgesamt</span></div>
          <div><b>${attrs.builtin_count ?? 0}</b><span>lokaler Grundkatalog</span></div>
          <div><b>${attrs.internet_count ?? 0}</b><span>Online-Katalog</span></div>
          <div><b>${attrs.imported_count ?? 0}</b><span>eigene Importe</span></div>
        </div>

        <main class="week">
          ${days.map((day, index) => this._dayCard(day, index)).join('')}
        </main>
      </div>
      ${this._modalRecipe ? this._recipeModal(this._modalRecipe, attrs.household_size) : ''}`;

    this.shadowRoot.querySelectorAll('[data-action]').forEach(element => {
      element.addEventListener('click', event => {
        if (element.classList.contains('modal-backdrop') && event.target !== element) return;
        this._handle(event.currentTarget);
      });
    });
  }

  _dayCard(day, index) {
    const selected = day.selected;
    const suggestions = day.suggestions || [];
    return `<section class="day ${selected ? 'planned' : ''}">
      <div class="dayhead">
        <div><h2>${this._esc(day.name)}</h2><span>${this._fmtDate(day.date)}</span></div>
        <button class="icon" title="${day.locked ? 'Entsperren' : 'Sperren'}" data-action="lock" data-day="${index}" data-locked="${day.locked ? 'false' : 'true'}">${day.locked ? '🔒' : '🔓'}</button>
      </div>
      ${selected ? this._selected(selected, day, index) : this._suggestions(suggestions, index)}
      <div class="dayactions">
        <button data-action="generate-day" data-day="${index}">↻ Andere Vorschläge</button>
        <button data-action="manual" data-day="${index}">✎ Freitext</button>
        ${selected ? `<button data-action="clear" data-day="${index}">× Leeren</button>` : ''}
      </div>
    </section>`;
  }

  _selected(recipe, day, index) {
    const tags = (recipe.tags || []).map(tag => `<span class="tag">${this._esc(this._tagName(tag))}</span>`).join('');
    const hasRecipe = (recipe.ingredients?.length || recipe.instructions?.length || recipe.url) && !day.manual;
    return `<div class="selected">
      <div class="check">✓</div>
      <div class="selectedbody">
        <small>GEWÄHLT${day.manual ? ' · FREITEXT' : ''}</small>
        <h3>${this._esc(recipe.name)}</h3>
        <div class="meta">${this._recipeMeta(recipe)}</div>
        <div class="tags">${tags}</div>
        ${hasRecipe ? `<button class="recipe-button" data-action="detail-selected" data-day="${index}">Rezept ansehen</button>` : ''}
      </div>
    </div>`;
  }

  _suggestions(items, dayIndex) {
    if (!items.length) {
      return `<div class="nosuggestions"><p>Noch keine Vorschläge.</p><span>Erzeuge drei passende Ideen für diesen Tag.</span></div>`;
    }
    return `<div class="suggestions">${items.map((recipe, index) => {
      const kind = index === 2 ? '✨ Besonders' : index === 0 ? '🏠 Einfach' : '🍽 Alternative';
      return `<article class="suggestion">
        ${recipe.image ? `<img src="${this._esc(recipe.image)}" loading="lazy" alt="">` : ''}
        <div class="suggestionbody">
          <small>${kind}</small>
          <h3>${this._esc(recipe.name)}</h3>
          <div class="meta">${this._recipeMeta(recipe)}</div>
          <div class="suggestion-actions">
            <button data-action="detail-suggestion" data-day="${dayIndex}" data-suggestion="${index}">Rezept</button>
            <button class="choose" data-action="select" data-day="${dayIndex}" data-suggestion="${index}">Auswählen</button>
          </div>
        </div>
      </article>`;
    }).join('')}</div>`;
  }

  _recipeModal(recipe, householdSize) {
    const tags = (recipe.tags || []).map(tag => `<span class="tag">${this._esc(this._tagName(tag))}</span>`).join('');
    const ingredients = (recipe.ingredients || []).map(item => `<li>${this._esc(item)}</li>`).join('');
    const instructions = (recipe.instructions || []).map((step, index) => `<li><span>${index + 1}</span><p>${this._esc(step)}</p></li>`).join('');
    const sourceButtons = [
      recipe.url ? `<button class="secondary" data-action="open-url" data-url="${this._esc(recipe.url)}">Originalquelle ↗</button>` : '',
      recipe.youtube ? `<button class="secondary" data-action="open-url" data-url="${this._esc(recipe.youtube)}">Video ↗</button>` : ''
    ].join('');
    const servingNote = recipe.servings
      ? `<span>${typeof recipe.servings === 'number' ? `${recipe.servings} Portionen` : this._esc(recipe.servings)}</span>`
      : `<span>${Number(householdSize) || 1} Portionen</span>`;

    return `<div class="modal-backdrop" data-action="close-detail">
      <section class="modal" role="dialog" aria-modal="true" aria-label="Rezeptdetails" data-modal="stop">
        <button class="modal-close" data-action="close-detail" aria-label="Schließen">×</button>
        ${recipe.image ? `<img class="hero" src="${this._esc(recipe.image)}" alt="">` : ''}
        <div class="modal-content">
          <div class="eyebrow">${this._esc(recipe.source || 'REZEPT')}</div>
          <h2>${this._esc(recipe.name)}</h2>
          ${recipe.description ? `<p class="description">${this._esc(recipe.description)}</p>` : ''}
          <div class="recipe-meta"><span>${recipe.minutes || 45} Min.</span>${servingNote}</div>
          <div class="tags">${tags}</div>

          ${ingredients ? `<div class="recipe-section"><h3>Zutaten</h3><ul class="ingredients">${ingredients}</ul></div>` : ''}
          ${instructions ? `<div class="recipe-section"><h3>Zubereitung</h3><ol class="instructions">${instructions}</ol></div>` : '<div class="recipe-section"><p>Für dieses Rezept sind keine Zubereitungsschritte hinterlegt.</p></div>'}

          <div class="modal-actions">
            ${sourceButtons}
            ${recipe.id ? `<button data-action="rate" data-rating="2">♥ Mag ich</button><button data-action="rate" data-rating="-1">Nicht so meins</button><button class="danger" data-action="block">Nicht mehr vorschlagen</button>` : ''}
          </div>
        </div>
      </section>
    </div>`;
  }

  _selectedRecipe(dayIndex) {
    return this._week().days?.[dayIndex]?.selected || null;
  }

  _suggestedRecipe(dayIndex, suggestionIndex) {
    return this._week().days?.[dayIndex]?.suggestions?.[suggestionIndex] || null;
  }

  async _handle(element) {
    const action = element.dataset.action;
    const day = Number(element.dataset.day);
    try {
      if (action === 'generate-week') await this._call('generate_week');
      if (action === 'generate-day') await this._call('generate_day', {day_index: day});
      if (action === 'select') await this._call('select_suggestion', {day_index: day, suggestion_index: Number(element.dataset.suggestion)});
      if (action === 'clear') await this._call('clear_day', {day_index: day});
      if (action === 'lock') await this._call('set_day_lock', {day_index: day, locked: element.dataset.locked === 'true'});
      if (action === 'manual') {
        const text = window.prompt('Essen für diesen Tag:');
        if (text?.trim()) await this._call('set_manual_meal', {day_index: day, text: text.trim()});
      }
      if (action === 'import') {
        const url = window.prompt('URL einer Rezeptseite:');
        if (url?.trim()) {
          await this._call('import_recipe_url', {url: url.trim()});
          window.alert('Das Rezept wurde importiert.');
        }
      }
      if (action === 'sync') {
        await this._call('refresh_internet');
        window.alert('Der Online-Katalog wurde synchronisiert.');
      }
      if (action === 'settings') window.location.href = '/config/integrations/integration/smart_meal_planner';
      if (action === 'open-url') window.open(element.dataset.url, '_blank', 'noopener');
      if (action === 'detail-selected') {
        this._modalRecipe = this._selectedRecipe(day);
        this.render();
      }
      if (action === 'detail-suggestion') {
        this._modalRecipe = this._suggestedRecipe(day, Number(element.dataset.suggestion));
        this.render();
      }
      if (action === 'close-detail') {
        if (element.dataset.modal === 'stop') return;
        this._modalRecipe = null;
        this.render();
      }
      if (action === 'rate' && this._modalRecipe?.id) {
        await this._call('rate_recipe', {recipe_id: this._modalRecipe.id, rating: Number(element.dataset.rating)});
      }
      if (action === 'block' && this._modalRecipe?.id) {
        if (window.confirm('Dieses Rezept künftig nicht mehr vorschlagen?')) {
          await this._call('block_recipe', {recipe_id: this._modalRecipe.id});
          this._modalRecipe = null;
          this.render();
        }
      }
    } catch (err) {
      window.alert(`Aktion fehlgeschlagen: ${err?.message || err}`);
    }
  }

  _style() {
    return `<style>
      :host{display:block;background:var(--primary-background-color);min-height:100%;color:var(--primary-text-color);font-family:var(--paper-font-body1_-_font-family,Roboto,Arial,sans-serif)}
      *{box-sizing:border-box}.page{max-width:1680px;margin:auto;padding:28px}header{display:flex;justify-content:space-between;gap:24px;align-items:flex-end;margin-bottom:22px}.eyebrow{font-size:11px;letter-spacing:.18em;font-weight:700;opacity:.55}h1{font-size:36px;margin:4px 0}header p{margin:0;opacity:.65}.actions{display:flex;gap:10px;flex-wrap:wrap}button{border:0;border-radius:12px;padding:10px 13px;background:var(--secondary-background-color);color:var(--primary-text-color);cursor:pointer;font-weight:600}button:hover{filter:brightness(1.06)}button.primary,.choose{background:var(--primary-color);color:var(--text-primary-color,#fff)}button.secondary{border:1px solid var(--divider-color)}button.danger{color:var(--error-color);border:1px solid color-mix(in srgb,var(--error-color) 35%,transparent)}
      .stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-bottom:18px}.stats>div{background:var(--card-background-color);border:1px solid var(--divider-color);border-radius:16px;padding:16px 18px;display:flex;flex-direction:column}.stats b{font-size:20px}.stats span{font-size:12px;opacity:.6;margin-top:3px}
      .week{display:grid;grid-template-columns:repeat(7,minmax(230px,1fr));gap:12px;overflow-x:auto;padding-bottom:12px}.day{min-width:230px;background:var(--card-background-color);border:1px solid var(--divider-color);border-radius:18px;padding:14px;display:flex;flex-direction:column;min-height:440px}.day.planned{border-color:color-mix(in srgb,var(--primary-color) 45%,var(--divider-color))}.dayhead{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}.dayhead h2{font-size:18px;margin:0}.dayhead span{font-size:12px;opacity:.55}.icon{padding:8px;background:transparent}
      .suggestions{display:flex;flex-direction:column;gap:9px}.suggestion{border:1px solid var(--divider-color);border-radius:14px;overflow:hidden;background:var(--primary-background-color)}.suggestion img{width:100%;height:92px;object-fit:cover}.suggestionbody{padding:10px}.suggestion small,.selected small{font-size:10px;font-weight:700;letter-spacing:.08em;opacity:.55}.suggestion h3,.selected h3{font-size:14px;line-height:1.25;margin:4px 0}.meta{font-size:11px;opacity:.6}.suggestion-actions{display:grid;grid-template-columns:1fr 1.25fr;gap:6px;margin-top:9px}.suggestion-actions button{padding:7px}
      .selected{display:flex;gap:12px;padding:16px 8px;flex:1}.check{width:32px;height:32px;flex:0 0 32px;border-radius:50%;display:grid;place-items:center;background:var(--primary-color);color:white;font-weight:800}.selectedbody{min-width:0}.selected h3{font-size:18px}.tags{display:flex;gap:5px;flex-wrap:wrap;margin-top:12px}.tag{font-size:10px;padding:4px 7px;border-radius:999px;background:var(--secondary-background-color)}.recipe-button{margin-top:14px;color:var(--primary-color);border:1px solid var(--divider-color);background:transparent}.nosuggestions{margin:auto 4px;text-align:center;opacity:.7}.nosuggestions p{font-weight:700;margin-bottom:4px}.nosuggestions span{font-size:12px}.dayactions{margin-top:auto;padding-top:12px;display:flex;flex-wrap:wrap;gap:6px;border-top:1px solid var(--divider-color)}.dayactions button{font-size:11px;padding:8px}.empty{max-width:600px;margin:80px auto;background:var(--card-background-color);padding:28px;border-radius:18px}
      .modal-backdrop{position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,.58);display:grid;place-items:center;padding:24px;overflow:auto}.modal{width:min(820px,100%);max-height:calc(100vh - 48px);overflow:auto;background:var(--card-background-color);border:1px solid var(--divider-color);border-radius:22px;position:relative;box-shadow:0 24px 70px rgba(0,0,0,.35)}.modal-close{position:absolute;right:14px;top:14px;z-index:2;width:38px;height:38px;padding:0;border-radius:50%;font-size:24px;background:rgba(0,0,0,.58);color:white}.hero{width:100%;height:260px;object-fit:cover}.modal-content{padding:26px}.modal-content h2{font-size:28px;margin:6px 0}.description{opacity:.75;line-height:1.55}.recipe-meta{display:flex;gap:14px;flex-wrap:wrap;font-size:13px;opacity:.65;margin:8px 0}.recipe-section{margin-top:26px}.recipe-section h3{margin:0 0 12px;font-size:18px}.ingredients{padding-left:20px;columns:2;column-gap:36px}.ingredients li{break-inside:avoid;margin:0 0 7px}.instructions{list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:12px}.instructions li{display:grid;grid-template-columns:30px 1fr;gap:10px;align-items:start}.instructions li>span{width:30px;height:30px;border-radius:50%;background:var(--secondary-background-color);display:grid;place-items:center;font-weight:700}.instructions p{margin:4px 0 0;line-height:1.55;white-space:pre-line}.modal-actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:28px;padding-top:18px;border-top:1px solid var(--divider-color)}
      @media(max-width:1100px){.stats{grid-template-columns:repeat(2,minmax(0,1fr))}}
      @media(max-width:900px){.page{padding:16px}header{align-items:flex-start;flex-direction:column}h1{font-size:30px}.stats{grid-template-columns:1fr 1fr}.week{grid-template-columns:1fr;overflow:visible}.day{min-height:0;min-width:0}.actions{width:100%}.actions button{flex:1}.suggestion{display:grid;grid-template-columns:90px 1fr}.suggestion img{height:100%;min-height:105px}.dayactions{margin-top:14px}.modal-backdrop{padding:10px}.modal{max-height:calc(100vh - 20px)}.hero{height:190px}.modal-content{padding:20px}.ingredients{columns:1}}
      @media(max-width:520px){.stats{grid-template-columns:1fr}.suggestion{grid-template-columns:1fr}.suggestion img{height:150px}.modal-content h2{font-size:23px}}
    </style>`;
  }
}

customElements.define('smart-meal-planner-panel', SmartMealPlannerPanel);
