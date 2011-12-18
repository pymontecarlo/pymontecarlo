package pymontecarlo.input.nistmonte;

import static org.junit.Assert.assertEquals;

import org.junit.Before;
import org.junit.Test;

public class TimeLimitTest {

    private TimeLimit limit;



    @Before
    public void setUp() throws Exception {
        limit = new TimeLimit(1234);
    }



    @Test
    public void testGetMaximumTime() {
        assertEquals(1234, limit.getMaximumTime());
    }

}
