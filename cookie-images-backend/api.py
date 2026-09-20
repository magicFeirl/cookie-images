from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db import DrawTable, close_db
from app.models.response import DrawResponse
from app.models.draw import DrawDocItem


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    close_db()
    print('DB CLOSED')


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root(pn: int = 0, ps: int = 20):
    mock_items = [
        DrawDocItem(
            poster_uid=343118157,
            title="Mock Title 1",
            description="これはモックデータです 1",
            pictures=["http://i0.hdslb.com/bfs/new_dyn/mock1.png"],
            count=1,
            ctime=1789879464,
            view=352,
            like=11,
            dyn_id="1250011851696111001",
        ),
        DrawDocItem(
            poster_uid=343118157,
            title="Mock Title 2",
            description="これはモックデータです 2",
            pictures=["http://i0.hdslb.com/bfs/new_dyn/mock2.jpg"],
            count=1,
            ctime=1789825053,
            view=354,
            like=10,
            dyn_id="1250011851696111002",
        ),
        DrawDocItem(
            poster_uid=343118157,
            title="Mock Title 3",
            description="これはモックデータです 3",
            pictures=["http://i0.hdslb.com/bfs/new_dyn/mock3.jpg"],
            count=1,
            ctime=1789811071,
            view=316,
            like=17,
            dyn_id="1250011851696111003",
        ),
    ]

    DrawTable.insert_many(mock_items)

    return DrawResponse(pn=pn, ps=ps, code=0, message="OK", data=mock_items)
