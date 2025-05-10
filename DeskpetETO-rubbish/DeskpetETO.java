package io.github.DeskpetETO;

import com.badlogic.gdx.ApplicationAdapter;
import com.badlogic.gdx.Gdx;
import com.badlogic.gdx.graphics.GL20;
import com.badlogic.gdx.graphics.g2d.TextureAtlas;
import com.esotericsoftware.spine.*;
import com.esotericsoftware.spine.utils.TwoColorPolygonBatch;

public class DeskpetETO extends ApplicationAdapter {
    private TwoColorPolygonBatch batch;
    private SkeletonRenderer renderer;
    private Skeleton skeleton;
    private AnimationState state;
    private TextureAtlas atlas;

    // 资源路径
    private static final String ATLAS_PATH = "spine/spineboy/spineboy-pma.atlas";
    private static final String JSON_PATH = "spine/spineboy/spineboy-pro.json";

    @Override
    public void create() {
        batch = new TwoColorPolygonBatch();
        renderer = new SkeletonRenderer();
        renderer.setPremultipliedAlpha(true); // 如果使用PMAs图集需要设置为true

        // 加载资源
        atlas = new TextureAtlas(Gdx.files.internal(ATLAS_PATH));
        SkeletonJson json = new SkeletonJson(atlas);
        json.setScale(0.6f); // 调整缩放比例

        SkeletonData skeletonData = json.readSkeletonData(Gdx.files.internal(JSON_PATH));
        skeleton = new Skeleton(skeletonData);
        skeleton.setPosition(300, 50); // 设置初始位置

        // 设置动画状态
        AnimationStateData stateData = new AnimationStateData(skeletonData);
        state = new AnimationState(stateData);
        state.setAnimation(0, "walk", true); // 使用你的动画名称
    }

    @Override
    public void render() {
        Gdx.gl.glClear(GL20.GL_COLOR_BUFFER_BIT);
        Gdx.gl.glClearColor(0.15f, 0.15f, 0.2f, 1f);

        float delta = Gdx.graphics.getDeltaTime();

        // 更新动画状态
        state.update(delta);
        state.apply(skeleton);
        skeleton.updateWorldTransform(Skeleton.Physics.update);

        // 开始渲染
        batch.getProjectionMatrix().setToOrtho2D(0, 0, Gdx.graphics.getWidth(), Gdx.graphics.getHeight());
        batch.begin();
        renderer.draw(batch, skeleton);
        batch.end();
    }

    @Override
    public void resize(int width, int height) {
        batch.getProjectionMatrix().setToOrtho2D(0, 0, width, height);
    }

    @Override
    public void dispose() {
        batch.dispose();
        atlas.dispose();
    }
}
