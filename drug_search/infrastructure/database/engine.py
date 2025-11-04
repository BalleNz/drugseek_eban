from typing import Final, AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from drug_search.config import config

DEBUG: Final[bool] = config.DEBUG
DATABASE_URL: Final[str] = config.DATABASE_URL


def create_async_db_engine_and_session(
        database_url: str,
        echo: bool,
        pool_size: int,
        max_overflow: int,
        pool_timeout: int,
        pool_recycle: int,
):
    engine = create_async_engine(
        url=database_url,
        echo=echo,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_timeout=pool_timeout,
        pool_recycle=pool_recycle,
        connect_args={
            "server_settings": {
                "timezone": "UTC",  # Явно указываем UTC для каждого соединения
            }
        }
    )
    return engine, async_sessionmaker(engine, expire_on_commit=False)


async def clear_metadata_cache():
    """Агрессивная очистка кеша метаданных SQLAlchemy"""
    try:
        print("🔄 Starting aggressive metadata cache clearance...")

        # 1. Полное пересоздание engine (самый эффективный способ)
        global engine, async_session_maker

        # Сохраняем настройки
        from drug_search.config import config
        DATABASE_URL = config.DATABASE_URL

        # Закрываем старый engine
        if engine:
            print("🔧 Disposing old engine...")
            await engine.dispose()

        # Даем время на полное закрытие соединений
        import asyncio
        await asyncio.sleep(1)

        # 2. Создаем совершенно новый engine
        print("🔧 Creating new engine...")
        new_engine = create_async_engine(
            url=DATABASE_URL,
            echo=False,  # Можно временно включить для отладки
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,
            connect_args={
                "server_settings": {
                    "timezone": "UTC",
                }
            }
        )

        # 3. Заменяем глобальные переменные
        engine = new_engine
        async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

        # 4. Принудительно обновляем метаданные через несколько запросов
        print("🔧 Refreshing metadata with test queries...")
        async with engine.connect() as conn:
            # трогаем структуру таблицы drugs
            await conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'drugs' 
                LIMIT 1
            """))

            # Еще один запрос для уверенности
            await conn.execute(text("SELECT COUNT(*) FROM drugs WHERE 1=0"))

            await conn.commit()

        # 5. Дополнительные методы очистки кеша SQLAlchemy
        try:
            # Очистка кеша компиляции
            if hasattr(engine, 'sync_engine'):
                if hasattr(engine.sync_engine, '_compiled_cache'):
                    engine.sync_engine._compiled_cache.clear()
                if hasattr(engine.sync_engine, '_schema_translate_map'):
                    engine.sync_engine._schema_translate_map = {}
        except Exception as cache_error:
            print(f"⚠️ Cache clearing warning: {cache_error}")

        # 6. Принудительный сборщик мусора
        import gc
        gc.collect()
        print("✅ Aggressive database metadata cache clearance completed successfully")

    except Exception as e:
        print(f"❌ Error during aggressive cache clearance: {e}")

engine, async_session_maker = create_async_db_engine_and_session(
    database_url=DATABASE_URL,
    echo=False,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session_generator:
        try:
            yield session_generator
        except Exception:
            await session_generator.rollback()
            raise
        finally:
            await session_generator.close()
