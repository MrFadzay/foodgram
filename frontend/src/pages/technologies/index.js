import { Title, Container, Main } from '../../components'
import styles from './styles.module.css'
import MetaTags from 'react-meta-tags'

const Technologies = () => {
  
  return <Main>
    <MetaTags>
      <title>О проекте</title>
      <meta name="description" content="Фудграм - Технологии" />
      <meta property="og:title" content="О проекте" />
    </MetaTags>
    
    <Container>
      <h1 className={styles.title}>Технологии</h1>
      <div className={styles.content}>
        <div>
          <h2 className={styles.subtitle}>Технологии, которые применены в этом проекте:</h2>
          <div className={styles.text}>
            <ul className={styles.textItem}>
              <li className={styles.textItem}>
                Python
              </li>
              <li className={styles.textItem}>
                Django
              </li>
              <li className={styles.textItem}>
                Django REST Framework
              </li>
              <li className={styles.textItem}>
                Djoser
              </li>
            </ul>
          </div>
        </div>
        <div>
          <h2 className={styles.subtitle}>Архитектура и ключевые компоненты</h2>
          <div className={styles.text}>
            <ul className={styles.textItem}>
              <li className={styles.textItem}>
                <b>Frontend:</b> React SPA, реализует пользовательский интерфейс и взаимодействует с API.
              </li>
              <li className={styles.textItem}>
                <b>Backend:</b> Django + Django REST Framework, реализует бизнес-логику, модели (Рецепт, Тег, Ингредиент, Пользователь), аутентификацию, фильтрацию, работу с избранным и списком покупок.
              </li>
              <li className={styles.textItem}>
                <b>Инфраструктура:</b> Docker, docker-compose, nginx, PostgreSQL, CI/CD через GitHub Actions.
              </li>
            </ul>
          </div>
          <h2 className={styles.subtitle}>Спецификация API</h2>
          <div className={styles.text}>
            <ul className={styles.textItem}>
              <li className={styles.textItem}>
                <b>Пользователи:</b> регистрация, получение профиля, смена аватара, авторизация.
              </li>
              <li className={styles.textItem}>
                <b>Рецепты:</b> создание, просмотр, редактирование, удаление, фильтрация по тегам, автору, избранному, списку покупок.
              </li>
              <li className={styles.textItem}>
                <b>Теги и ингредиенты:</b> получение списков, фильтрация.
              </li>
              <li className={styles.textItem}>
                <b>Избранное и список покупок:</b> добавление/удаление рецептов, скачивание списка покупок.
              </li>
            </ul>
            <p className={styles.textItem}>
              Подробная спецификация доступна в формате OpenAPI (YAML) в папке <code>docs/</code> проекта.
            </p>
          </div>
        </div>
      </div>
      
    </Container>
  </Main>
}

export default Technologies

